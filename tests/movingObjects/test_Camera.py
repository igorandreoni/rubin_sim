import numpy as np
import unittest
import os
from rubin_sim.data import get_data_dir
from rubin_sim.movingObjects import BaseObs


class TestCamera(unittest.TestCase):

    def setUp(self):
        obj_ra = np.array([10.0, 12.1], float)
        obj_dec = np.array([-30.0, -30.0], float)
        obj_mjd = np.array([59580.16, 59580.16], float)
        self.ephems = np.array(list(zip(obj_ra, obj_dec, obj_mjd)),
                               dtype=([('ra', float), ('dec', float), ('mjd', float)]))
        obs_ra = np.array([10.0, 10.0], float)
        obs_dec = np.array([-30.0, -30.0], float)
        obs_mjd = np.array([59580.16, 59580.16], float)
        obs_rotSkyPos = np.zeros(2)
        self.obs = np.array(list(zip(obs_ra, obs_dec, obs_rotSkyPos, obs_mjd)),
                            dtype=([('ra', float), ('dec', float), ('rotSkyPos', float), ('mjd', float)]))

    def testCameraFov(self):
        obs = BaseObs(obsRA='ra', obsDec='dec', obsTimeCol='mjd', footprint='camera',
                      camera_footprint_file=os.path.join(get_data_dir(), 'tests', 'fov_map.npz'))
        idxObs = obs.ssoInCameraFov(self.ephems, self.obs)
        self.assertEqual(idxObs, [0])


if __name__ == "__main__":
    unittest.main()
