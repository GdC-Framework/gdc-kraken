from django.test import TestCase
from django.contrib.auth.models import User
from gdc_storm.models import Mission, MapName, Player, GameSession, GameSessionPlayer

class MissionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.map = 'altis'

    def test_str_returns_name(self):
        mission = Mission.objects.create(
            name="CPC-CO[20]-TestMission",
            user=self.user,
            authors="Auteur",
            max_players=20,
            type="CO",
            pbo_file="missions/test.pbo",
            version="1",
            map=self.map
        )
        self.assertEqual(str(mission), "CPC-CO[20]-TestMission")

    def test_save_invalid_name(self):
        mission = Mission(
            name="BadName",
            user=self.user,
            authors="Auteur",
            max_players=20,
            type="CO",
            pbo_file="missions/test.pbo",
            version="1",
            map=self.map
        )
        with self.assertRaises(ValueError):
            mission.save()

class MapNameModelTest(TestCase):
    def test_str_returns_display_name(self):
        mapname = MapName.objects.create(code_name="altis", display_name="Altis")
        self.assertEqual(str(mapname), "Altis")

class PlayerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')

    def test_str_returns_name(self):
        player = Player.objects.create(name="John Doe")
        self.assertEqual(str(player), "John Doe")
        player.users.add(self.user)
        self.assertIn(self.user, player.users.all())

class GameSessionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.mission = Mission.objects.create(
            name="CPC-CO[20]-TestMission",
            user=self.user,
            authors="Auteur",
            max_players=20,
            type="CO",
            pbo_file="missions/test.pbo",
            version="1",
            map="altis"
        )

    def test_str(self):
        session = GameSession.objects.create(mission=self.mission, version="1", start_time="2025-06-12T12:00:00Z")
        self.assertIn("CPC-CO[20]-TestMission", str(session))

class GameSessionPlayerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.player = Player.objects.create(name="John Doe")
        self.mission = Mission.objects.create(
            name="CPC-CO[20]-TestMission",
            user=self.user,
            authors="Auteur",
            max_players=20,
            type="CO",
            pbo_file="missions/test.pbo",
            version="1",
            map="altis"
        )
        self.session = GameSession.objects.create(mission=self.mission, version="1", start_time="2025-06-12T12:00:00Z")

    def test_str(self):
        gsp = GameSessionPlayer.objects.create(session=self.session, player=self.player, role="Chef", status="VIVANT")
        self.assertIn("John Doe", str(gsp))
        self.assertIn("Chef", str(gsp))
        self.assertIn("VIVANT", str(gsp))
