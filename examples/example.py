
"""
Tests out the new and improved variable solver
"""

# standard libraries
import time
from collections import Counter
from operator import mul
from sys import argv

# nonstandard libraries
from scipy.misc import comb
import matplotlib.pyplot as plt
from matplotlib import cm

# intrapackage libraries
from madhype import simulate_run
#from defaults import general_options as default_options

        

#------------------------------------------------------------------------------# 

""" Main Callable Method """
#------------------------------------------------------------------------------# 

if __name__ == "__main__":

    """ Use command line arguments """
    
    if len(argv) > 1:
        mode = int(argv[1])
        print 'User set mode to {}...'.format(mode)
        time.sleep(1.0)
    else:
        mode = 1
        print 'Default mode set to {}...'.format(mode)
        time.sleep(1.0)

    if mode == 1:
        
        options = {
              # experimental design
              'num_wells':(96,),
              'cpw':(100,),
#              'analysis':('madhype',),
              # simulated repertoire
              'num_cells':500,
              'seed':1,
              'cell_freq_distro':'power-law',
              'cell_freq_constant':1.0,
              'chain_misplacement_prob':0.0, # TODO: add functionality
              'chain_deletion_prob':0.1,
              'alpha_dual_prob':          0.,
              'beta_dual_prob':           0.,
              'alpha_sharing_probs':     None,
              'beta_sharing_probs':      None,
#              # madhype analysis constants
#              'threshold':0.1, # minimum ratio accepted by match_probability
#              'fdr':0.01, # acceptable fdr (cuts off matches, sets filter)
#              'prior_alpha':1.0, # prior for clonal frequency
#              'prior_match':1.0, # prior for clonal match ( <= 1.0 )
#              # alphabetr analysis constants
#              'iters':100,
#              'pair_threshold':0.95,
              # visual cues
              'silent':False,
              'visual':True,
              'compare':False,
              }
        solvers = ['madhype']
        solver_options = [{
            'threshold': 0.1, # minimum ratio accepted by match_probability
            'fdr': 0.01, # acceptable fdr (cuts off matches, sets filter)
            'prior_alpha': 1.0, # prior for clonal frequency
            'prior_match': 1.0 # prior for clonal match
        }]

        print 'Starting on seed {}...'.format(options['seed'])
        results = simulate_run(solvers, solver_options, **options)

#        '''
#        start = 9
#        total = 2
#        print 'Starting {} - {}'.format(start,start+total-1)
#        for i in xrange(start,start+total):
#            #if i == 9:
#            #    options['compare'] = True
#            results = simulate_system(options,seed=i)
#        #'''#

    if mode == 2:
    
        # system parameters
        repeats = 50
        cpw_range = np.logspace(0,4,41,dtype=int)
        #num_wells_range = [12,24,36,48]
        num_wells_range = [60,72,84,96]

        # simulation parameters
        options = {
                'num_cells':1000,
                'num_wells':(24,),
                'seed':1,
                'silent':True
                }

        id_map = np.zeros((len(cpw_range),options['num_cells']))

        for ii,num_wells in enumerate(num_wells_range): 
            for i,cpw in enumerate(cpw_range):
                for seed in xrange(repeats):
                    results = test(options,cpw=(cpw,),seed=seed,num_wells=(num_wells,))
                    id_map[i,:] += results['pattern']
                print 'Finished cpw = {}!'.format(cpw)

            # display graph
            c_labels = [v for v in [1,10,100,1000,10000] if v <= max(cpw_range)]
            c_inds = [min(range(len(cpw_range)), key=lambda i: abs(cpw_range[i]-v)) for v in c_labels]

            fig, ax = plt.subplots()

            cax = ax.imshow(id_map,interpolation='nearest')
            ax.set_aspect(aspect='auto')

            ax.set_yticks(c_inds)
            ax.set_yticklabels(c_labels)

            plt.title('Identification of clones with {} wells'.format(num_wells))
            plt.xlabel('Clonal Index')
            plt.ylabel('Cells per well (#)')
            cbar = fig.colorbar(cax, ticks=[0,repeats])
            cbar.ax.set_yticklabels(['0%','100%'])  # vertically oriented colorbar
            
            fig.savefig('{}_wells.eps'.format(num_wells),format='eps',dpi=1000)

        # show, allow user to exit
        plt.show(block=False)
        raw_input('Press enter to close...')
        plt.close()


    if mode == 3:
        ''' Generates conserved cell count experiment '''
        options = {
                'num_cells':1000,
                'cell_freq_max':0.01,
                'cell_freq_constant':1,
                # visual cues
                'silent':True,
                'visual':False
                }
        T = 96000
        W = 48
        #w_range = [24,48,72]
        w_range = [0,6,12,18,24,30,36,42,48]
        c_range = np.logspace(0,3,16,dtype=int)
        repeats = 3

        id_map = np.zeros((len(c_range),len(w_range)))

        for i,c in enumerate(c_range):
            for j,w in enumerate(w_range):
                for seed in xrange(repeats):
                    #print 'Starting cpw = {}, num_wells = {}'.format((c,int((T - c*w)/(W-w))),(w,W-w))
                    results = test(options,cpw=(c,int((T - c*w)/(W-w))),seed=seed,num_wells=(w,W-w))
                    id_map[i,j] += results['frac_repertoire']
                print 'Finished w1 = {}!'.format(w)
            print 'Finished c1 = {}!'.format(c)

        # normalize fraction of repertoires
        id_map /= repeats

        c_labels = [v for v in [1,10,100] if v <= max(c_range)]
        c_inds = [min(range(len(c_range)), key=lambda i: abs(c_range[i]-v)) for v in c_labels]

        fig, ax = plt.subplots() # create blank figure
        cax = ax.imshow(id_map,interpolation='nearest',vmin=0,vmax=1.0) # fill with heatmap
        ax.set_aspect(aspect='auto') # fix aspect ratios

        plt.title('Fixed cell count = {}'.format(T))
        plt.xlabel('# wells in partition')
        plt.ylabel('# cells/well in partition')

        ax.set_xticks([i for i in xrange(len(w_range))])
        ax.set_xticklabels(w_range)

        ax.set_yticks(c_inds)
        ax.set_yticklabels(c_labels)

        # colorbar in action
        cbar = plt.colorbar(cax,ax=ax,ticks=[0,1])
        cbar.ax.set_yticklabels(['0%','100%'])  # vertically oriented colorbar

        # show, allow user to exit
        plt.show(block=False)
        raw_input('Press enter to close...')
        plt.close()

