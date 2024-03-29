import tellurium as te

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os
import pandas as pd

import math
def is_eigen_oscillator(r, f=None, writeoupath=None):
    hasgoodvals = False
    # 1. Measure eigen values
    # eigens = r.getFullEigenValues()
    # hasgoodvals = check_eigens(eigens)
    # if hasgoodvals:
    #     return True
    # 2. If that didn't work, measure steady state
    try:
        r.steadyState()
        eigens = r.getFullEigenValues()
        hasgoodvals = check_eigens(eigens)
        if hasgoodvals:
            if r.S0 < 0 or r.S1 < 0 or r.S2 < 0:
                return False
            else:
                return True
    except:
        pass
    # 3. If that didn't work, simulate for a bit
    r.reset()
    try:
        r.simulate(0, 50, 100000)

    except:
        try:
            r.integrator.relative_tolerance = 1e-10
            r.reset()
            r.simulate(0, 50, 100000)
        except:
            return False
    try:
        eigens = r.getFullEigenValues()
    except:
        return False
    hasgoodvals = check_eigens(eigens)
    if hasgoodvals:
        return True
    # 4. If that still didn't work, calculate steady state again
    try:
        r.steadyState()
        eigens = r.getFullEigenValues()
        hasgoodvals = check_eigens(eigens)
    except:
        pass
    # And if that doesn't work then it's definitely (?) not an oscillator
    return hasgoodvals

def check_eigens(eigen_array):
    for num in eigen_array:
        if num.real >= 0 and num.imag != 0:
            return True
    return False

def plot_several_models_and_savefig(filepath, outpath, rows, cols):
    total = len(os.listdir(filepath))
    num_rounds = math.ceil(total/(rows*cols))
    idx = 0
    models = []
    model_names = []
    for dir in os.listdir(filepath):
        parentdir = os.path.join(filepath, dir)
        fullpath = os.path.join(parentdir, "final_models")
        for model_file in os.listdir(fullpath):
            if model_file.startswith("bestmodel"):
                f = open(os.path.join(fullpath, model_file), "r")
                astr = f.read()
                f.close()
                models.append(astr)
                model_names.append(parentdir[-15:])
    for rnd in range(num_rounds):

        fig, axs = plt.subplots(rows, cols)
        for i in range(rows):
            if idx >= total:
                plt.savefig(os.path.join(outpath, f"{rnd}"), dpi=5000)
                plt.clf()
                break
            for j in range(cols):
                r = te.loada(models[idx])
                try:
                    m = r.simulate(0)
                    r.steadyState()
                    axs[i, j].plot(m['time'], m[:, 1:])
                    axs[i, j].set_title(f"{model_names[idx]}\n{has_oscillator_eigens(r.getFullEigenValues())}", size=8)
                except:
                    pass
                idx += 1
                if idx >= total:
                    plt.savefig(os.path.join(outpath, f"{rnd}"), dpi=5000)
                    plt.clf()
                    break
        plt.show()
        plt.savefig(os.path.join(outpath, f"{rnd}"))
        plt.clf()
    print("done")

# def manually_check_oscillators(inpath, outpath, unsure):
#     for file in os.listdir(inpath):
#         fullpath = os.path.join(inpath, file)
#         f = open(fullpath, "r")
#         astr = f.read()
#         f.close()
#         r = te.loada(astr)
#         try:
#             r.simulate(0,50,10000)
#         except:
#             try:
#                 r.integrator.relative_tolerance = 1e-10
#                 r.reset()
#                 r.simulate(0, 50, 100000)
#             except:
#                 out = os.path.join(outpath, f"cantsim_{file}")
#                 f_out = open(out, "w")
#                 r.reset()
#                 f_out.write(r.getCurrentAntimony())
#                 f_out.close()
#         r.plot()
#         isoscillator = input("Is this an oscillator?")
#         if isoscillator == "y":
#             f_out = os.path.join(outpath, file)
#         elif isoscillator =="u":
#             f_out = os.path.join(unsure, file)
#         else:
#             continue
#         f_out = open(out, "w")
#         r.reset()
#         f_out.write(r.getCurrentAntimony())
#         f_out.close()

def gather_best_models(inputpath, outputpath):
    if not os.path.isdir(outputpath):
        os.makedirs(outputpath)
    models_evaluated = 0
    oscillators = 0
    for file in os.listdir(inputpath): # Eg. 2024-02-24T12:03:00.332
        fullpath = os.path.join(inputpath, f"{file}/final_models")
        for model_file in os.listdir(fullpath):
            if model_file.startswith("best"):
                f = open(os.path.join(fullpath, model_file), "r")
                astr = f.read()

def plot_several_models(filepath, rows, cols):
    fig, axs = plt.subplots(rows, cols)
    models = []
    model_names = []
    fitnesses = []
    cwd = os.getcwd()
    cwd = os.path.join(cwd, "src")
    for file in os.listdir(filepath):
        model_names.append(file[6:])
        fullpath = os.path.join(filepath, file)
        fullpath = os.path.join(cwd, fullpath)
        f = open(fullpath, "r")
        astr = f.read()
        models.append(astr)
        for line in astr.split("\n"):
            if line.startswith("#fit"):
                fitness = line.split(" ")[1]
                fitnesses.append(fitness)
        f.close()
    idx = 0
    for i in range(rows):
        if idx >= len(model_names):
            break
        for j in range(cols):
            m = 0
            if "Lw1" in model_names[idx]:
                print("here")
            r = te.loada(models[idx])
            has_eigs = is_eigen_oscillator(r)
            r.reset()
            try:
                m = r.simulate(0,50, 1000)
                # try:
                #     r.reset()
                #     r.steadyState()
                #     eigs = r.getFullEigenValues()
                #     has_eigs = has_oscillator_eigens(eigs)
                # except:
                #     has_eigs = "N/A"

            except:
                try:
                    r.integrator.relative_tolerance = 1e-10
                    r.reset()
                    m = r.simulate(0, 50, 100000)
                except:
                    print(model_names[idx])
            if not isinstance(m, int):
                axs[i, j].plot(m['time'], m[:, 1:])
                axs[i, j].set_title(f"{model_names[idx]} \n{has_eigs}\n{fitnesses[idx][:7]}", size=8)
            else:
                axs[i, j].set_title(f"{model_names[idx]} \n{has_eigs}\n{fitnesses[idx][:7]}", size=8)
            idx += 1
            if idx >= len(models):
                break
    plt.subplots_adjust(wspace=0.5, hspace=0.8)
    plt.show()

def has_oscillator_eigens(eigenvals):
    for num in eigenvals:
        if num.real > 0 and num.imag != 0:
            return True
    return False


# path ="/home/hellsbells/Desktop/networkEv/src/final_models"
# plot_several_models(path, 5, 2)

def make_truth_csv(model, filename, simulation=[0, 1, 10]):
    if not filename.endswith(".csv"):
        filename += ".csv"
    cwd = os.getcwd()
    path = os.path.join(cwd, f"test_files/{filename}")
    r = te.loada(model)
    result = r.simulate(simulation[0], simulation[1], simulation[2])
    df = pd.DataFrame(result, columns=['time']+r.getFloatingSpeciesIds())
    df.set_index('time', inplace=True)
    df.to_csv(path)

def plot_single_model(model, simulation=[0, 1, 10]):
    r = te.loada(model)
    r.simulate(simulation[0], simulation[1], simulation[2])
    r.plot()

def compare_model_plots(truthmodel, evolvedmodel, simulation=[0, 1, 10]):
    r1 = te.loada(truthmodel)
    result1 = r1.simulate(simulation[0], simulation[1], simulation[2])

    r2 = te.loada(evolvedmodel)
    result2 = r2.simulate(simulation[0], simulation[1], simulation[2])

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1, title="Truth Model")
    ax2 = fig.add_subplot(1, 2, 2, title="Evolved Model")#, sharey=ax1)
    ax2.set_ylim(0,20)
    ax1.plot(result1[:, 0], result1[:, 1:])
    ax2.plot(result2[:, 0], result2[:, 1:])
    ax1.legend(r1.getFloatingSpeciesIds())
    ax2.legend(r2.getFloatingSpeciesIds())
    plt.show()


import json
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
import os
import tellurium as te


def plot_fitness(path):
    f = open(path)
    data = json.load(f)
    f.close()
    fitness = data["top_individual_fitness"]
    plt.plot(fitness)
    plt.show()

def plot_several_fitness(path):
    for dir in os.listdir(path):
        fullpath = os.path.join(path, f"{dir}/datatracker.json")
        try:
            f = open(fullpath)
            data = json.load(f)
            f.close()
            fitness = data["top_individual_fitness"]
            plt.plot(fitness)
        except:
            continue
    plt.title(path)
    plt.show()

def find_descreasing_fitness(path):
    for dir in os.listdir(path):
        fullpath = os.path.join(path, f"{dir}/datatracker.json")
        try:
            f = open(fullpath)
            data = json.load(f)
            f.close()
            fitness = data["top_individual_fitness"]
            for i in range(len(fitness)-2):
                if fitness[i + 1] < fitness[i]:
                    print(dir, i)
                    break

        except:
            continue




inputpath = "/home/hellsbells/Desktop/evolution_output/800gen_nostalls_success"
# outputpath = inputpath + "_success"
# plot_several_fitness(inputpath)
# find_descreasing_fitness(inputpath)


# for file in os.listdir(path):
#     f = open(os.path.join(path, file), "r")
#     astr = f.read()
#     f.close()
#     r = te.loada(astr)
#     if not is_eigen_oscillator(r):
#         print(file)
#
#
# plot_several_models(inputpath,4, 4)
# # #

# path = "/home/hellsbells/Desktop/networkEv/Data/BenchmarkTests/1000_trials_oscillators"
# modelname = "bestmodel_H4Pyg4D9SZ5i"
#
# model_path = os.path.join(path, modelname)
#
# f = open(model_path, "r")
# astr = f.read()
# f.close()
# r = te.loada(astr)
# r.simulate(0, 1, 100)
# print(r.getFullEigenValues())
# r.plot()

r = te.loada("""
// Created by libAntimony v2.12.0
// Compartments and Species:
species S1, S2, S0;

// Reactions:
_J0: S1 + S2 -> S0 + S2; k1*S1*S2;
#_J1: S0 + S0 -> S2; k2*S0*S0;
_J2: S0 + S0 -> S0; k3*S0*S0;
_J3: S0 + S1 -> S1 + S1; k4*S0*S1;
_J4: S1 -> S1 + S2; k5*S1;
_J5: S0 + S2 -> S0 + S2; k6*S0*S2;
_J6: S0 -> S0 + S2; k7*S0;
_J7: S1 + S1 -> S1 + S1; k8*S1*S1;
_J8: S2 -> S2; k9*S2;
_J9: S1 -> S0 + S1; k10*S1;
_J10: S0 -> S2 + S2; k11*S0;
_J11: S0 + S2 -> S2; k12*S0*S2;
_J12: S1 -> S0 + S0; k13*S1;
_J13: S2 -> S0; k14*S2;
_J14: S1 -> S1; k15*S1;

// Species initializations:
S1 = 5;
S2 = 9;
S0 = 1;

// Variable initializations:
k1 = 3.36495487244513;
k2 = 9.3887511062499;
k3 = 19.8324490541693;
k4 = 59.9610897219989;
k5 = 41.3953222290076;
k6 = 10.8446618226208;
k7 = 85.1925626785795;
k8 = 47.9051148402496;
k9 = 14.6363835222696;
k10 = 9.39312395219087;
k11 = 57.856294625205;
k12 = 9.13869907614637;
k13 = 28.1911480471516;
k14 = 29.0559217184585;
k15 = 44.0058206837288;

// Other declarations:
const k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15;

#fitness: 0.050921741969524786
""")
# r.integrator.relative_tolerance = 1e-10
# r.reset()
# m = r.simulate(0, 50, 100000)
r.simulate(0, 10,500)
r.plot()
# r.reset()
# r.steadyState()
# print(r.S0, r.S1, r.S2)
# r.reset()
print(is_eigen_oscillator(r))
# r.reset()
# r.steadyState()
# # print(r.S0, r.S1, r.S2)
# print(r.getFullEigenValues())
#
# r.reset()
# r.integrator.relative_tolerance = 1e-10
# # r.reset()
# r.simulate(0, 10, 100)
# r.plot()
# #
# # r.steadyState()
# # print(r.getFullEigenValues())
# # r.reset()
# # fig, axs = plt.subplots(1, 3)
# #
#
# print(r.getFullEigenValues())
# m = r.simulate(0,10,500)
# axs[0].plot(m['time'], m[:,1:])
# axs[0].set_title(f"{r.getFullEigenValues()}", size=8)
#
# r.reset()
# m = r.simulate(0,1000,5000)
# axs[1].plot(m['time'], m[:,1:])
# axs[1].set_title(f"{r.getFullEigenValues()}", size=8)
#
# r.reset()
# m = r.simulate(0,10000,50000)
# axs[2].plot(m['time'], m[:,1:])
# axs[2].set_title(f"{r.getFullEigenValues()}", size=8)
# plt.show()