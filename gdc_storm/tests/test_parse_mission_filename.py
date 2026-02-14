import unittest
from gdc_storm.utils import parse_mission_filename

class TestParseMissionFilename(unittest.TestCase):
    def test_valid_filename(self):
        filename = 'CPC-CO[20]-TestMission-V2.altis.pbo'
        result = parse_mission_filename(filename)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'CPC-CO[20]-TestMission')
        self.assertEqual(result[1], 'CO')
        self.assertEqual(result[2], '20')
        self.assertEqual(result[3], 'V2')
        self.assertEqual(result[4], 'altis')

    def test_invalid_filename(self):
        invalid_filenames = [
            'badname.pbo',
            'CPC-CO[20]-TestMission-V2.pbo',
            'CPC-CO[20]-TestMission-V2.altis',
            'CPC-CO[20]-TestMission-V2.altis.pbo.extra',
            'CPC-CO[1]-TestMission-V2.altis.pbo',
        ]
        for filename in invalid_filenames:
            with self.subTest(filename=filename):
                result = parse_mission_filename(filename)
                self.assertIsNone(result)

    def test_wrong_type(self):
        filename = 'CPC-XX[20]-TestMission-V2.altis.pbo'
        result = parse_mission_filename(filename)
        self.assertIsNone(result)

    def test_missing_version(self):
        filename = 'CPC-CO[20]-TestMission.altis.pbo'
        result = parse_mission_filename(filename)
        self.assertIsNone(result)

    def test_three_digit_players(self):
        filename = 'CPC-CO[100]-BigMission-V1.altis.pbo'
        result = parse_mission_filename(filename)
        self.assertIsNotNone(result)
        self.assertEqual(result[2], '100')

if __name__ == '__main__':
    unittest.main()
