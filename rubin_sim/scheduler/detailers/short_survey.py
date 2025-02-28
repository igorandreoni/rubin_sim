from rubin_sim.scheduler.detailers import Base_detailer
from rubin_sim.utils import _raDec2Hpid, m5_flat_sed
import rubin_sim.scheduler.features as features
from rubin_sim.scheduler.utils import hp_in_lsst_fov
import numpy as np
import healpy as hp
import matplotlib.pylab as plt

__all__ = ['Short_expt_detailer']


class Short_expt_detailer(Base_detailer):
    """Check if the area has been observed with a short exposure time this year. If not, add some short exposures.

    Parameters
    ----------
    exp_time : `float` (1.)
        The short exposure time to use.
    nobs : `float` (2)
        The number of observations to try and take per year
    night_max : `float` (None)
        Do not apply any changes to the observation list if the current night is greater than night_max.
    n_repeat : `int` (1)
        How many short observations to do in a row.

    """
    def __init__(self, exp_time=1., filtername='r', nside=32, footprint=None, nobs=2,
                 mjd0=59853.5, survey_name='short', read_approx=2., night_max=None, n_repeat=1):
        self.read_approx = read_approx
        self.exp_time = exp_time
        self.filtername = filtername
        self.nside = nside
        self.footprint = footprint
        self.nobs = nobs
        self.survey_name = survey_name
        self.mjd0 = mjd0
        self.night_max = night_max
        self.n_repeat = n_repeat

        self.survey_features = {}
        # XXX--need a feature that tracks short exposures in the filter
        self.survey_features['nobs'] = features.N_observations(filtername=filtername, nside=nside,
                                                               survey_name=self.survey_name)
        # Need to be able to look up hpids for each observation
        self.obs2hpid = hp_in_lsst_fov(nside=nside)

    def __call__(self, observation_list, conditions):

        # XXX--this logic would probably make more sense as a feasability basis function.
        # Might consider expanding the detailer base class to include basis functions.
        if self.night_max is not None:
            if conditions.night > self.night_max:
                return observation_list

        out_observations = []
        # Compute how many observations we should have taken by now
        n_goal = self.nobs * np.round((conditions.mjd - self.mjd0)/365.25 + 1)
        time_to_add = 0.
        for observation in observation_list:
            out_observations.append(observation)
            if observation['filter'] == self.filtername:
                hpids = self.obs2hpid(observation['RA'], observation['dec'])
                # Crop off anything outside the target footprint
                hpids = hpids[np.where(self.footprint[hpids] > 0)]
                # Crop off things where we already have enough observation
                hpids = hpids[np.where(self.survey_features['nobs'].feature[hpids] < n_goal)]
                if np.size(hpids) > 0:
                    for i in range(0, self.n_repeat):
                        new_obs = observation.copy()
                        new_obs['exptime'] = self.exp_time
                        new_obs['nexp'] = 1
                        new_obs['note'] = self.survey_name
                        out_observations.append(new_obs)
                        time_to_add += new_obs['exptime'] + self.read_approx
        # pump up the flush time
        for observation in observation_list:
            observation['flush_by_mjd'] += time_to_add/3600./24.
        return out_observations
