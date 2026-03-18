import random
import secrets

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from gdc_storm.models import ApiToken, GameSession, GameSessionPlayer, MapName, Mission, Player


class Command(BaseCommand):
    help = "Genere des donnees fictives coherentes (DEV) : maps, missions, joueurs, sessions."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Efface d'abord les donnees de dev (missions/sessions/joueurs/maps).")
        parser.add_argument("--seed", type=int, default=None, help="Graine aleatoire (pour regenerer les memes donnees).")

        parser.add_argument("--maps", type=int, default=5, help="Nombre de cartes MapName a generer.")
        parser.add_argument("--missions", type=int, default=12, help="Nombre de missions a generer.")
        parser.add_argument("--players", type=int, default=35, help="Nombre de joueurs a generer.")
        parser.add_argument("--sessions", type=int, default=18, help="Nombre de GameSession a generer.")
        parser.add_argument("--players-per-session-min", type=int, default=4, help="Nb joueurs min par session.")
        parser.add_argument("--players-per-session-max", type=int, default=12, help="Nb joueurs max par session.")

        parser.add_argument("--create-demo-user", dest="create_demo_user", action="store_true", default=True,
                            help="Creer/mettre a jour un utilisateur de demo (pour proprietaire des missions).")
        parser.add_argument("--no-create-demo-user", dest="create_demo_user", action="store_false",
                            help="Ne pas creer d'utilisateur de demo.")
        parser.add_argument("--demo-username", type=str, default="demo_maker", help="Username du user de demo.")
        parser.add_argument("--demo-password", type=str, default="demo_maker", help="Mot de passe du user de demo.")

        parser.add_argument("--api-token", dest="api_token", action="store_true", default=True,
                            help="Creer/mettre a jour un token API pour tester les endpoints.")
        parser.add_argument("--no-api-token", dest="api_token", action="store_false",
                            help="Ne pas creer de token API.")
        parser.add_argument("--api-token-name", type=str, default="dev_token", help="Nom du ApiToken.")
        parser.add_argument("--api-token-key", type=str, default=None, help="Clé ApiToken fixe (sinon generée). Doit faire <= 64 caracteres.")

    def handle(self, *args, **options):
        if not getattr(settings, "DEBUG", False):
            self.stderr.write(self.style.WARNING("DEBUG est False : generation recommandée uniquement en DEV."))
            self.stderr.write(self.style.WARNING("Passez PLATFORM=DEV pour activer DEBUG, ou ajoutez manuellement votre seed si besoin."))

        seed = options["seed"]
        if seed is not None:
            random.seed(seed)

        maps_count = max(0, int(options["maps"]))
        missions_count = max(0, int(options["missions"]))
        players_count = max(0, int(options["players"]))
        sessions_count = max(0, int(options["sessions"]))

        players_per_session_min = max(1, int(options["players_per_session_min"]))
        players_per_session_max = max(players_per_session_min, int(options["players_per_session_max"]))

        demo_user = None
        if options["create_demo_user"]:
            demo_user = self._get_or_create_demo_user(
                username=options["demo_username"],
                password=options["demo_password"],
            )

        api_token_key = None
        if options["api_token"]:
            api_token_key = self._get_or_create_api_token(
                token_name=options["api_token_name"],
                token_key=options["api_token_key"],
            )

        with transaction.atomic():
            if options["clear"]:
                self._clear_dev_data()

            map_objs = self._generate_maps(maps_count)
            mission_objs = self._generate_missions(missions_count=missions_count, map_objs=map_objs, demo_user=demo_user)
            player_objs = self._generate_players(players_count=players_count, demo_user=demo_user)
            self._generate_sessions(
                sessions_count=sessions_count,
                missions=mission_objs,
                players=player_objs,
                players_per_session_min=players_per_session_min,
                players_per_session_max=players_per_session_max,
            )

        self.stdout.write(self.style.SUCCESS("Données fictives DEV générées avec succès."))
        if api_token_key:
            self.stdout.write(f"ApiToken.key = {api_token_key}")

    def _clear_dev_data(self):
        # Ordre : GameSessionPlayer -> GameSession -> Mission -> Player -> MapName (MapName n'est pas FK sur Mission).
        GameSessionPlayer.objects.all().delete()
        GameSession.objects.all().delete()
        Mission.objects.all().delete()
        Player.objects.all().delete()
        MapName.objects.all().delete()

    def _get_or_create_demo_user(self, username: str, password: str):
        group, _ = Group.objects.get_or_create(name="Mission Maker")
        user, created = User.objects.get_or_create(username=username, defaults={"is_active": True})
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
        user.groups.add(group)
        return user

    def _get_or_create_api_token(self, token_name: str, token_key: str | None):
        if token_key:
            if len(token_key) > 64:
                raise ValueError("api-token-key doit faire <= 64 caracteres (contrainte ApiToken.key).")
        else:
            # token_hex(32) => 64 caracteres hex
            token_key = secrets.token_hex(32)

        token, created = ApiToken.objects.get_or_create(key=token_key, defaults={"name": token_name, "is_active": True})
        if not created:
            token.name = token_name
            token.is_active = True
            token.save(update_fields=["name", "is_active"])
        return token_key

    def _generate_maps(self, maps_count: int):
        # Liste raisonnable de codes de cartes (coherents avec l'affichage de l'app).
        known_maps = [
            ("altis", "Altis"),
            ("tanoa", "Tanoa"),
            ("chernarus", "Chernarus"),
            ("sara", "Sara"),
            ("enoch", "Enoch"),
            ("namalsk", "Namalsk"),
            ("livonia", "Livonia"),
            ("cup", "CUP Maps"),
            ("theaters", "Theaters"),
            ("winter", "Winter"),
        ]

        map_objs = []
        for i in range(maps_count):
            if i < len(known_maps):
                code_name, display_name = known_maps[i]
            else:
                code_name, display_name = f"map{i+1:02d}", f"Map {i+1:02d}"

            code_name = (code_name or "").strip().lower()
            if not code_name:
                code_name = f"map{i+1:02d}"

            obj, _ = MapName.objects.get_or_create(code_name=code_name, defaults={"display_name": display_name})
            # Assure que display_name existe même si on a déjà une MapName créée.
            if obj.display_name != display_name:
                obj.display_name = display_name
                obj.save(update_fields=["display_name"])
            map_objs.append(obj)
        return map_objs

    def _generate_missions(self, missions_count: int, map_objs: list[MapName], demo_user: User | None):
        mission_type_choices = [code for code, _label in Mission.TYPE_CHOICES]
        status_choices = [code for code, _label in Mission.STATUS_CHOICES]

        # Titres sans '.', car le parseur (mission.sqm filename attendu) en tient compte.
        title_by_type = {
            "CO": ["Operation_Alpha", "Raid_RedSun", "Coop_Strike", "Keep_Watch", "Bridge_Breach"],
            "TVT": ["Arena_Showdown", "Storm_Route", "Siege_Line", "Clash_Overlord", "Target_Training"],
            "GM": ["Ghost_Recon", "Night_Op", "Recon_Overpass", "Urban_Assault", "Iron_Silence"],
            "HC": ["Hardcore_Challenge", "HiCom_Protocol", "Helix_Charge", "Signal_Breach", "Cold_Start"],
            "TRAINING": ["Training_Bootcamp", "Skill_Run", "Drill_Dawn", "Tutorial_Path", "Practice_Stage"],
            "COM": ["Community_Mission", "Comms_Break", "Cache_Protocol", "Relay_Rendezvous", "Signal_Transfer"],
        }

        authors_pool = [
            "Sparfell",
            "Apoc",
            "Ashrak",
            "bluth",
            "Eagletres4",
            "Elma",
            "Izual",
            "Pataplouf",
            "Random",
            "Zey",
        ]

        if not map_objs:
            raise RuntimeError("Aucune MapName generee : augmente --maps ou lance la commande avec un nombre > 0.")

        missions = []
        for _i in range(missions_count):
            mission_type = random.choice(mission_type_choices)
            max_players = random.randint(10, 90)  # 2 chiffres min (regex CPC-XX[YY]-)
            min_players = random.randint(5, max_players - 1) if max_players > 6 else None
            if min_players is not None and min_players >= max_players:
                min_players = max_players - 1

            title = random.choice(title_by_type.get(mission_type, ["Mission_Temp"]))
            mission_name = f"CPC-{mission_type}[{max_players}]-{title}"

            version_num = random.randint(1, 9)
            status = random.choice(status_choices)

            map_obj = random.choice(map_objs)
            authors = random.choice(authors_pool)

            briefing = [
                {
                    "name": "Objectif",
                    "content": f"<p>Maintenir la position sur <b>{map_obj.display_name}</b> et atteindre la zone cible.</p>",
                },
                {
                    "name": "Notes",
                    "content": "<p>Ce contenu est genere pour le developpement (faux, mais coherent).</p>",
                },
            ]

            # Dans l'app, l'upload cherche une mission par (name, map, max_players).
            existing = Mission.objects.filter(name=mission_name, map=map_obj.code_name, max_players=max_players).first()
            if existing:
                mission = existing
                mission.user = demo_user
                mission.authors = authors
                mission.min_players = min_players
                mission.type = mission_type
                mission.version = str(version_num)
                mission.status = status
                mission.publication_date = timezone.now()
                mission.onLoadMission = "Chargement... Verifier les coordonnees et preparer l'equipe."
                mission.overviewText = "Bienvenue dans une mission de developpement (donnees fictives)."
                mission.briefing = briefing
                mission.save()
            else:
                mission = Mission.objects.create(
                    name=mission_name,
                    user=demo_user,
                    authors=authors,
                    min_players=min_players,
                    max_players=max_players,
                    type=mission_type,
                    version=str(version_num),
                    map=map_obj.code_name,
                    status=status,
                    onLoadMission="Chargement... Verifier les coordonnees et preparer l'equipe.",
                    overviewText="Bienvenue dans une mission de developpement (donnees fictives).",
                    briefing=briefing,
                )
            missions.append(mission)

        return missions

    def _generate_players(self, players_count: int, demo_user: User | None):
        first_names = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Giga", "Hawk", "Iris", "Joker", "Kilo", "Lima"]
        last_names = ["Fox", "Tango", "Nova", "Viper", "Orion", "Raven", "Saber", "Cobra", "Atlas", "Comet", "Drift", "Storm"]

        players = []
        for i in range(players_count):
            # Noms deterministes-ish : plus stable visuellement.
            name = f"{random.choice(first_names)}_{random.choice(last_names)}_{i+1:03d}"

            player, _created = Player.objects.get_or_create(name=name)
            players.append(player)

            if demo_user and i < min(players_count, 12):
                player.users.add(demo_user)

        return players

    def _generate_sessions(
        self,
        sessions_count: int,
        missions: list[Mission],
        players: list[Player],
        players_per_session_min: int,
        players_per_session_max: int,
    ):
        if not missions:
            return
        if not players:
            return

        verdict_codes = [code for code, _label in GameSession.VERDICT_CHOICES]
        role_pool = [
            "Rifleman",
            "Medic",
            "Engineer",
            "Sniper",
            "Spotter",
            "Assault",
            "Support",
            "Marksman",
        ]

        living_status = "VIVANT"
        dead_status = "MORT"

        sessions = []
        for i in range(sessions_count):
            mission = random.choice(missions)
            verdict = random.choice(verdict_codes)

            duration_min = random.randint(8, 75)
            start_time = timezone.now() - timezone.timedelta(days=random.randint(0, 20), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            end_time = start_time + timezone.timedelta(minutes=duration_min) if random.random() > 0.12 else None

            version_suffix = random.randint(1, 9)
            session_name = f"{mission.name}-V{version_suffix}"

            session = GameSession.objects.create(
                mission=mission,
                name=session_name,
                map=mission.map,
                version=str(mission.version),
                start_time=start_time,
                end_time=end_time,
                verdict=verdict,
            )
            sessions.append(session)

        # Création des GameSessionPlayer en batch.
        gsp_to_create: list[GameSessionPlayer] = []
        for session in sessions:
            n_players = random.randint(players_per_session_min, players_per_session_max)
            n_players = min(n_players, len(players))
            session_players = random.sample(players, k=n_players)

            for p in session_players:
                role = random.choice(role_pool)
                status = living_status if random.random() > 0.22 else dead_status
                gsp_to_create.append(
                    GameSessionPlayer(
                        session=session,
                        player=p,
                        role=role,
                        status=status,
                    )
                )

        if gsp_to_create:
            GameSessionPlayer.objects.bulk_create(gsp_to_create, batch_size=500)

