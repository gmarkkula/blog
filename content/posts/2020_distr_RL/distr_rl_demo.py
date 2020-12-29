import math
import random
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
from celluloid import Camera

FONTSIZE = 14


def adjust_lightness(color, amount):
    """
    from https://stackoverflow.com/questions/37765197/darken-or-lighten-a-color-in-matplotlib
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])


class DistrRLDemo:

    def get_sample(self, i_distribution):
        i = random.randrange(self.n_gaussians[i_distribution])
        return random.normalvariate(self.mus[i_distribution][i], self.sigmas[i_distribution][i])

    def __init__(self, mus, sigmas, estimators, learn_rate, n_samples):
        """
            mus and sigmas: lists with one item per distribution, each item a tuple defining 
            a number of peaks in the distribution.
            estimators: either an int specifying the number of estimators, or a tuple of quantiles
            learn_rate: average learning rate of estimators
            n_samples: number of observations to draw from the distributions
        """

        # init 
        # - set default plot settings
        self.set_plot_settings()
        # - store info about the distributions to learn from
        # -- number of distributions
        self.n_distributions = len(mus)
        assert len(sigmas) == self.n_distributions
        # -- peaks in each distribution
        self.n_gaussians = []
        self.mus = []
        self.sigmas = []
        for i_distr in range(self.n_distributions):   
            self.n_gaussians.append(len(mus[i_distr]))
            assert len(sigmas[i_distr]) == self.n_gaussians[i_distr]
            self.mus.append(np.array(mus[i_distr]))
            self.sigmas.append(np.array(sigmas[i_distr]))
        # - get the quantiles to estimate
        if type(estimators) == tuple:
            # user has provided a tuple of quantiles to use
            self.n_estimators = len(estimators)
            self.quantiles = np.array(estimators)
        else:
            assert type(estimators) == int
            # user has specified the number of quantiles to use
            self.n_estimators = estimators
            self.quantiles = np.linspace(0, 1, self.n_estimators+2)[1:-1]
        # - get the learning rates for the estimators (scaled so as to sum to 
        #   2 x learn_rate)
        self.pos_learn_rates = 2 * learn_rate * self.quantiles
        self.neg_learn_rates = 2 * learn_rate * (1 - self.quantiles)
        # - more storing
        self.n_samples = n_samples
        self.n_anim_frames = 2 * n_samples

        # run the distributional RL
        # - prepare arrays for storing the results
        self.estimator_expectations = \
            np.full((self.n_distributions, self.n_samples, self.n_estimators), math.nan)
        self.estimator_expectations[:, 0, :] = 0
        self.prediction_errors = \
            np.full((self.n_distributions, self.n_samples, self.n_estimators), math.nan)
        self.samples = np.full((self.n_distributions, self.n_samples), math.nan)
        # - loop through the requested number of learning time steps
        for i in range(self.n_samples-1):
            # loop through the distributions being learned from
            for i_distr in range(self.n_distributions):
                # draw a sample from the distribution 
                self.samples[i_distr, i] = self.get_sample(i_distr)
                # calculate prediction errors for the estimators
                self.prediction_errors[i_distr, i, :] = \
                    self.samples[i_distr, i] - self.estimator_expectations[i_distr, i, :]
                # which estimators had positive/negative prediction errors?
                idx_pos_errors = np.argwhere(self.prediction_errors[i_distr, i, :] >= 0)
                idx_neg_errors = np.argwhere(self.prediction_errors[i_distr, i, :] < 0)
                # update the estimator expectations
                self.estimator_expectations[i_distr, i+1, idx_pos_errors] = \
                    self.estimator_expectations[i_distr, i, idx_pos_errors] \
                    + self.pos_learn_rates[idx_pos_errors] 
                self.estimator_expectations[i_distr, i+1, idx_neg_errors] = \
                    self.estimator_expectations[i_distr, i, idx_neg_errors] \
                    - self.neg_learn_rates[idx_neg_errors] 
    

    def set_plot_settings(self, 
        plot_samples = True, plot_ests = True, plot_quantiles = False, 
        plot_pdf = False, plot_cdf = False, 
        plot_xticks = True, plot_only_zero_xtick = True, plot_yticks = True, 
        plot_xlabel = None, plot_ylabel = None, 
        distr_colors = None, distr_labels = None, distr_label_xs = None, distr_label_ys = None,
        lr_plot_scaling = None, est_spacing = None, xlim = None):

        self.plot_samples = plot_samples
        self.plot_ests = plot_ests
        self.plot_quantiles = plot_quantiles
        self.plot_pdf = plot_pdf
        self.plot_cdf = plot_cdf
        self.plot_xticks = plot_xticks
        self.plot_only_zero_xtick = plot_only_zero_xtick
        self.plot_yticks = plot_yticks
        self.plot_xlabel = plot_xlabel
        self.plot_ylabel = plot_ylabel
        self.distr_colors = distr_colors
        self.distr_labels = distr_labels
        self.distr_label_xs = distr_label_xs
        self.distr_label_ys = distr_label_ys
        self.lr_plot_scaling = lr_plot_scaling
        self.est_spacing = est_spacing
        self.xlim = xlim


    def get_plot_xlims(self):

        if self.xlim is None:
            N_PLOT_STDDEVS = 4
            plotmin_x = math.inf
            plotmax_x = -math.inf
            for i_distr in range(self.n_distributions):
                this_plotmin_x = min(self.mus[i_distr] - N_PLOT_STDDEVS * self.sigmas[i_distr])
                this_plotmax_x = max(self.mus[i_distr] + N_PLOT_STDDEVS * self.sigmas[i_distr])
                plotmin_x = min(plotmin_x, this_plotmin_x)
                plotmax_x = max(plotmax_x, this_plotmax_x)
        else:
            plotmin_x = self.xlim[0]
            plotmax_x = self.xlim[1]
        return (plotmin_x, plotmax_x)


    def plot_snapshot(self, axes = None, n_data_samples = None, n_learned_samples = None):

        # larger font size
        plt.rc('font', size=FONTSIZE)  

        # need to create an axes for plotting?
        if axes is None:
            fig, axes = plt.subplots()

        # plot colours provided?
        if self.distr_colors is None:
            self.distr_colors = []
            for i_distr in range(self.n_distributions):
                self.distr_colors.append('blue')

        # plot the end result if no specific sample requested by user
        if n_data_samples is None:
            n_data_samples = self.n_samples
        if n_learned_samples is None:
            n_learned_samples = self.n_samples-1

        # get a good x plot range
        (plotmin_x, plotmax_x) = self.get_plot_xlims()

        # loop over the distributions and plot
        maxYs = [] # for keeping track of max Y output and to set the y limits accordingly
        for i_distr in range(self.n_distributions):

            base_color = self.distr_colors[i_distr]
            dark_color = adjust_lightness(base_color, 0.9)
            maxYs.append(-math.inf)

            # plot the actual samples obtained?
            if self.plot_samples:
                N_BINS = 50
                bin_width = (plotmax_x - plotmin_x) / N_BINS
                unscaled_area = self.n_samples * bin_width
                bin_counts, bin_edges = np.histogram(self.samples[i_distr, :n_data_samples], \
                    bins=N_BINS, range=(plotmin_x, plotmax_x))
                sample_bar_heights = bin_counts / unscaled_area
                axes.bar(bin_edges[:-1], sample_bar_heights, width=bin_width, align='edge', \
                    color=base_color, alpha=0.3)
                # what will the sample bar heights be at the last sample?
                final_bin_counts, __ = np.histogram(self.samples[i_distr, :], bins=N_BINS, \
                    range=(plotmin_x, plotmax_x))
                final_sample_bar_heights = final_bin_counts / unscaled_area
                maxYs[i_distr] = max(maxYs[i_distr], max(final_sample_bar_heights))
            # get the true pdf and cdf for the distribution
            distr_x = np.linspace(plotmin_x, plotmax_x, 500)
            distr_pdf = np.zeros(distr_x.size)
            for i in range(self.n_gaussians[i_distr]):
                distr_pdf += scipy.stats.norm.pdf(distr_x, self.mus[i_distr][i], self.sigmas[i_distr][i]) \
                    / self.n_gaussians[i_distr]
            maxYs[i_distr] = max(maxYs[i_distr], max(distr_pdf))
            distr_cdf = np.cumsum(np.diff(distr_x) * distr_pdf[1:])
            # get (and possibly plot) the true locations of the sought quantiles for this distribution
            true_quantiles = np.full(self.n_estimators, math.nan)
            for i in range(self.n_estimators):
                true_quantile_idx = np.argwhere(distr_cdf >= self.quantiles[i])[0]
                true_quantiles[i] = distr_x[true_quantile_idx]
                if self.plot_quantiles:
                    if self.plot_cdf:
                        axes.plot(np.array((plotmin_x, true_quantiles[i])), np.full(2, self.quantiles[i]), \
                            '--', color = base_color, lw = 1)
                        axes.plot(np.full(2, true_quantiles[i]), np.array((0, self.quantiles[i])), \
                            '--', color = base_color, lw = 1)
                    elif self.plot_pdf:
                        axes.plot(np.full(2, true_quantiles[i]), np.array((0, distr_pdf[true_quantile_idx])), \
                            '--', color = base_color, lw = 1)
                    else:
                        axes.plot(np.full(2, true_quantiles[i]), np.array((0, max(distr_pdf)/6)), \
                            '--', color = base_color, lw = 1)
            # plot the true pdf and cdf?
            if self.plot_pdf:
                MIN_PLOT_PDF = 0.001
                distr_pdf_hi = np.copy(distr_pdf)
                distr_pdf_hi[np.argwhere(distr_pdf < MIN_PLOT_PDF)] = math.inf
                axes.plot(distr_x, distr_pdf_hi, color = base_color, lw = 2)
            if self.plot_cdf:
                axes.plot(distr_x[:-1], distr_cdf, '--', color = base_color, lw = 1.5)
            # y coords for estimator plotting
            if self.est_spacing is None:
                est_ys = np.zeros(self.n_estimators)
            else:
                est_ys = np.arange(self.n_estimators) * self.est_spacing
            # plot the estimator expectations at the specified sample?
            if self.plot_ests:
                axes.plot(self.estimator_expectations[i_distr, n_learned_samples, :], \
                    est_ys, 'o', markersize=6, color=base_color)
            # plot the learning rates per estimator?
            if not self.lr_plot_scaling is None:
                for i_est in range(self.n_estimators):
                    est_x = self.estimator_expectations[i_distr, n_learned_samples, i_est]
                    est_y = est_ys[i_est]
                    est_lrs = np.array((-self.neg_learn_rates[i_est], self.pos_learn_rates[i_est]))
                    axes.plot(est_x + self.lr_plot_scaling * est_lrs, np.full(2, est_y), '-', \
                        color=base_color, lw=1.5)
                    axes.plot(est_x + self.lr_plot_scaling * est_lrs[0], est_y, '<', \
                        color=base_color, markersize=4)
                    axes.plot(est_x + self.lr_plot_scaling * est_lrs[1], est_y, '>', \
                        color=base_color, markersize=4)

        # set x limits
        axes.set_xlim((plotmin_x, plotmax_x))
        # set y limits
        if self.plot_cdf:
            max_y = 1
        else:
            max_y = max(maxYs) # max of pdfs and samples (if plotted)
        ZOOM_FACTOR = 0.05
        plotmin_y = -max_y * ZOOM_FACTOR
        plotmax_y = max_y * (1 + ZOOM_FACTOR)
        axes.set_ylim((plotmin_y, plotmax_y))
        # distribution labels?
        if not (self.distr_labels is None):
            for i_distr, label in enumerate(self.distr_labels):
                label_x = self.distr_label_xs[i_distr]
                label_y = self.distr_label_ys[i_distr] * max_y
                axes.text(label_x, label_y, label, color = self.distr_colors[i_distr], 
                    fontweight = 'medium', horizontalalignment = 'center')
        # axis ticks?
        axes.spines['right'].set_visible(False)
        axes.spines['top'].set_visible(False)
        if not self.plot_xticks:
            axes.tick_params(axis='x', bottom=False, labelbottom=False)
        elif self.plot_only_zero_xtick:
            axes.set_xticks((0,))
        if not self.plot_yticks:
            axes.tick_params(axis='y', left=False, labelleft=False)
        # axis labels?
        if not self.plot_xlabel is None:
            axes.set_xlabel(self.plot_xlabel)
        if not self.plot_ylabel is None:
            axes.set_ylabel(self.plot_ylabel)
        # axis lines?
        if (self.plot_xlabel is None) and (not self.plot_xticks):
            axes.spines['bottom'].set_visible(False)
        if (self.plot_ylabel is None) and (not self.plot_yticks):
            axes.spines['left'].set_visible(False)
        
        plt.tight_layout()

    
    def plot_estimator_trajectories(self, axes = None):

        # init
        plt.rc('font', size=FONTSIZE)  
        if axes is None:
            fig, axes = plt.subplots()

        for i_distr in range(self.n_distributions):
            for i in range(self.n_estimators):
                axes.plot(self.estimator_expectations[i_distr, :, i], 
                    np.arange(self.n_samples), color = self.distr_colors[i_distr])



    def get_n_samples_for_anim_frame(self, i_frame):
        assert i_frame >= 0 and i_frame <= self.n_anim_frames-1
        n_data_samples = math.ceil(i_frame/2)
        n_learned_samples = math.floor(i_frame/2)
        return (n_data_samples, n_learned_samples)
    

    def save_gif(self, file_name, rl_frame_step = 1, gif_frame_rate=10):
        fig, axes = plt.subplots()
        camera = Camera(fig)
        for i_frame in range(0, self.n_anim_frames, rl_frame_step):
            n_data_samples, n_learned_samples = \
                self.get_n_samples_for_anim_frame(i_frame)
            self.plot_snapshot(axes=axes, n_data_samples=n_data_samples, n_learned_samples=n_learned_samples)
            camera.snap()
        animation = camera.animate()
        animation.save(file_name, writer="imagemagick", fps=gif_frame_rate)



