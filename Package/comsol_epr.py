import os
import sys

sys.path.append("../../Package/")
from comsol_client import ComsolClient

import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 7})
cm = 1/2.54

import numpy as np
from matplotlib.gridspec import GridSpec
import scipy.constants as con

#%%
phi0 = con.value('mag. flux quantum')/(2*con.pi)

#%%
mph_file = r"C:\Users\chenq7\PycharmProjects\QCDComsol\Design\Wavepool\model_6.mph"
client = ComsolClient()
model = client.load_model(mph_file)

model.param().param()

#%% inspect model
LJ_list = []
for name in model.param().param():
    if name[:2] == 'LJ':
        LJ_list.append(float(model.param().get(name)))

LJ_list = np.array(LJ_list)
EJ_list = (phi0**2)/LJ_list

# print(model.physics())
# print(model.studies())
#
# #%%
eval_node = model.result().numerical().create("sev1", "EvalGlobal")
eval_node.set("expr", "emw.freq")
f_list = np.squeeze(eval_node.getReal())

eval_node.set("expr", "emw.Qfactor")
Q_list = np.squeeze(eval_node.getReal())

eval_node.set("expr", "emw.intWe")
P_electric = np.squeeze(eval_node.getReal())

eval_node.set("expr", "emw.intWm")
P_magnetic = np.squeeze(eval_node.getReal())

P_mat = []
for num_port in range(10):
    try:
        eval_node.set("expr", "emw.Pport_" + str(num_port+1))
        P_mat.append(np.squeeze(eval_node.getReal()))
    except:
        break

P_mat = np.array(P_mat)
kappa_mat = -P_mat/(P_electric+P_magnetic)
Q_mat = (2*np.pi*f_list)/kappa_mat

#%% participation ratio
p_mat = []
# phi_mat = []
for num_JJ in range(len(LJ_list)):
    val_LJ = LJ_list[num_JJ]
    val_EJ = EJ_list[num_JJ]

    key_I = 'emw.Ielement_' + str(num_JJ + 1)
    eval_node.set("expr", key_I)
    val_I = np.squeeze(eval_node.getReal()) + 1j*np.squeeze(eval_node.getImag())

    key_We = 'emw.intWe'
    eval_node.set("expr", key_We)
    val_We = np.squeeze(eval_node.getReal())

    val_p = np.sign(np.imag(val_I)) * (np.abs(val_I) ** 2) * val_LJ  / (4*val_We)
    # val_phi = np.sign(np.imag(val_I)) * np.sqrt(np.abs(val_p) * (con.h * f_list)/(2*val_EJ))

    # normalize
    val_p = val_p/np.sum(np.abs(val_p))
    p_mat.append(val_p)
    # phi_mat.append(val_phi)

p_mat = np.array(p_mat)
sgn_mat = np.sign(p_mat)
# phi_mat = np.array(phi_mat)

#%% Hamiltonian
Chi_mat = np.zeros((len(f_list), len(f_list)))
for num_1 in range(len(f_list)):
    for num_2 in range(len(f_list)):
        Chi_mat[num_1, num_2] = (con.h/4) * f_list[num_1] * f_list[num_2] * np.sum(np.abs(p_mat[:, num_1]) * np.abs(p_mat[:, num_2])/EJ_list)

Delta_list = (1/2) * np.sum(Chi_mat, axis=1)
Alpha_list = (1/2) * np.diag(Chi_mat)

#%%
fig = plt.figure(figsize = (18*cm,9*cm), constrained_layout=True)
gs = GridSpec(nrows=1, ncols=4, figure=fig, width_ratios=[len(f_list),1,len(LJ_list),len(Q_mat)])

# quality factor
ax3 = fig.add_subplot(gs[3])
ax3.pcolormesh(np.log10(Q_mat.T), vmin=0, vmax=10, cmap='RdBu_r')
for (i,j),label in np.ndenumerate(Q_mat):
    label2 = '{:.3f}'.format(np.log10(label))
    ax3.text(i+0.5,j+0.5,label2,ha='center',va='center', color='k')

ax3.set_yticks([])
ax3.set_xticks(np.linspace(0.5, len(Q_mat)-0.5, len(Q_mat)),
           np.linspace(1, len(Q_mat), len(Q_mat), dtype=int))
ax3.set_xlabel('Port')

secay = ax3.secondary_yaxis('right')
secay.set_yticks(np.linspace(0.5, len(f_list)-0.5, len(f_list)),
           ['{:.3f}'.format(f) for f in np.log10(Q_list)],
           color='gray')

ax3.set_title('Q factor (log10)', fontsize=7)

# participation ratio
ax0 = fig.add_subplot(gs[2])
ax0.pcolormesh(p_mat.T, vmin=-1, vmax=1, cmap='RdBu_r')
for (i,j),label in np.ndenumerate(p_mat):
    label2 = '{:.3f}'.format(label)
    ax0.text(i+0.5,j+0.5,label2,ha='center',va='center', color='k')

ax0.set_yticks([])
ax0.set_xticks(np.linspace(0.5, len(LJ_list)-0.5, len(LJ_list)),
           np.linspace(1, len(LJ_list), len(LJ_list), dtype=int))
ax0.set_xlabel('Junction')

secay = ax0.secondary_yaxis('right')
secay.set_yticks(np.linspace(0.5, len(f_list)-0.5, len(f_list)),
           ['{:.3f}'.format(f) for f in np.sum(np.abs(p_mat), axis=0)],
           color='gray')

# secax = ax0.secondary_xaxis('top')
# secax.set_xticks(np.linspace(0.5, len(LJ_list)-0.5, len(LJ_list)),
#                  ['{:.3f}'.format(val) for val in np.sum(np.abs(p_mat), axis=1)],
#                  rotation='vertical', color='gray')

ax0.set_title('Participation', fontsize=7)

# Delta
ax1 = fig.add_subplot(gs[1])
ax1.pcolormesh(np.transpose([np.log10(Delta_list)]), vmin=0, vmax=9, cmap='Blues')
for (i,j),label in np.ndenumerate([Delta_list]):
    label2 = '{:.3f}'.format(label / 1e6)
    ax1.text(i+0.5,j+0.5,label2,ha='center',va='center', color='k')

ax1.set_xticks([])
ax1.set_yticks([])
# ax1.set_xlabel('Shift')
ax1.set_title('Shift (MHz)', fontsize=7)

# Chi
ax2 = fig.add_subplot(gs[0])

Chi_mat2 = Chi_mat.copy()
np.fill_diagonal(Chi_mat2, Alpha_list)

ax2.pcolormesh(np.log10(Chi_mat2), vmin=0, vmax=9, cmap='Blues')
for (j,i),label in np.ndenumerate(Chi_mat2):
    label2 = '{:.3f}'.format(label/1e6)
    ax2.text(i+0.5,j+0.5,label2,ha='center',va='center', color='k')

ax2.set_xticks(np.linspace(0.5, len(f_list)-0.5, len(f_list)),
           ['{:.3f}'.format(f) for f in f_list/1e9],
           rotation=90)
ax2.set_xlabel('Eigenfrequency (GHz)')

ax2.set_yticks(np.linspace(0.5, len(f_list)-0.5, len(f_list)),
           ['{:.3f}'.format(f) for f in f_list/1e9])
ax2.set_ylabel('Eigenfrequency (GHz)')

ax2.set_title('Kerr coupling (MHz)', fontsize=7)

fig.align_labels()
plt.savefig(mph_file + '.pdf', bbox_inches='tight')
plt.show()