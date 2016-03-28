#!/usr/bin/env python

import subprocess

import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt

query_mass = """SELECT tl.Time AS Time,IFNULL(sub.qty, 0) AS Quantity
FROM timelist as tl
LEFT JOIN (
SELECT tl.Time as time,SUM(inv.Quantity) AS qty
FROM inventories as inv
JOIN timelist as tl ON UNLIKELY(inv.starttime <= tl.time) AND inv.endtime > tl.time AND tl.simid=inv.simid
JOIN agents as a on a.agentid=inv.agentid AND a.simid=inv.simid
WHERE a.simid=? AND a.prototype=? 
GROUP BY tl.Time
) AS sub ON sub.time=tl.time
WHERE tl.simid=?
"""

query_239 = """SELECT tl.Time AS Time,IFNULL(sub.qty, 0) AS Quantity FROM timelist as tl
LEFT JOIN (
        SELECT tl.Time as time,SUM(inv.Quantity*c.MassFrac) AS qty
        FROM inventories as inv
        JOIN timelist as tl ON UNLIKELY(inv.starttime <= tl.time) AND inv.endtime > tl.time AND tl.simid=inv.simid
        JOIN agents as a on a.agentid=inv.agentid AND a.simid=inv.simid
        JOIN compositions as c on c.qualid=inv.qualid AND c.simid=inv.simid
        WHERE a.simid=? AND a.prototype=?  AND c.nucid = 942390000
        GROUP BY tl.Time
) AS sub ON sub.time=tl.time
WHERE tl.simid=?"""

query_built = """SELECT tl.time AS Time,ifnull(sub.n, 0) AS N_Built
FROM timelist AS tl
LEFT JOIN (
SELECT a.simid,tl.time AS time,COUNT(a.agentid) AS n
FROM agents AS a
JOIN timelist AS tl ON tl.time=a.entertime
WHERE a.simid=? AND a.prototype=?
GROUP BY time
) AS sub ON tl.time=sub.time AND tl.simid=sub.simid
WHERE tl.simid=?
"""

query_receiver_flow = """SELECT tl.Time AS Time,TOTAL(sub.qty) AS Quantity
FROM timelist as tl
LEFT JOIN (
SELECT t.simid AS simid,t.time as time,SUM(c.massfrac*r.quantity) as qty
FROM transactions AS t
JOIN resources as r ON t.resourceid=r.resourceid AND r.simid=t.simid
JOIN agents as send ON t.senderid=send.agentid AND send.simid=t.simid
JOIN agents as recv ON t.receiverid=recv.agentid AND recv.simid=t.simid
JOIN compositions as c ON c.qualid=r.qualid AND c.simid=r.simid
WHERE t.simid=?  AND recv.prototype=? AND t.commodity=?  
GROUP BY t.time
) AS sub ON tl.time=sub.time AND tl.simid=sub.simid
WHERE tl.simid=?
GROUP BY tl.Time;
"""

query_sender_flow = """SELECT tl.Time AS Time,TOTAL(sub.qty) AS Quantity
FROM timelist as tl
LEFT JOIN (
SELECT t.simid AS simid,t.time as time,SUM(c.massfrac*r.quantity) as qty
FROM transactions AS t
JOIN resources as r ON t.resourceid=r.resourceid AND r.simid=t.simid
JOIN agents as send ON t.senderid=send.agentid AND send.simid=t.simid
JOIN agents as recv ON t.receiverid=recv.agentid AND recv.simid=t.simid
JOIN compositions as c ON c.qualid=r.qualid AND c.simid=r.simid
WHERE t.simid=? AND send.prototype=?  AND t.commodity=?  
GROUP BY t.time
) AS sub ON tl.time=sub.time AND tl.simid=sub.simid
WHERE tl.simid=?
GROUP BY tl.Time;
"""

def post_dbs(dbs):
    for name in dbs:
        cmd = "cyan -db {}.sqlite post".format(name)
        subprocess.call(cmd.split(), shell=False)

def time_series(protos, query):
    series = []
    for name, kinds in protos.items():
        con = sql.connect('{}.sqlite'.format(name))
        cur = con.cursor()
        
        info = cur.execute('SELECT * from INFO').fetchall()
        simid = info[0][0]
        
        x, y = None, None
        for kind in kinds:
            args = [simid, kind, simid] if not isinstance(kind, list) else \
                [simid] + kind + [simid]
            data = np.array(cur.execute(query, args).fetchall())
            x = data[:, 0] if x is None else x
            if y is not None:
                y += data[:, 1]
            else:
                y = data[:, 1]
        series.extend([x, y])
    return series

def plot_pu_in_rxtrs(protos, args):
    plt.clf()
    plt.plot(*args)
    # plt.title('Inventory in All Reactors')
    plt.ylabel('Mass of $^{239}Pu$ (kg)')
    plt.xlabel('Timesteps (months)')
    plt.legend(list(protos.keys()))
    plt.tight_layout()
#    plt.show()
    plt.savefig('figs/pu_in_rxtrs.png')

def plot_pu_in_fabs(protos, args, zoom=False):
    plt.clf()
    plt.plot(*args)
    plt.title('Inventory of $^{239}Pu$ in Recycled-Fuel Fabrication Facilities')
    plt.ylabel('Mass (kg)')
    plt.xlabel('Timesteps (months)')
    plt.legend(list(protos.keys()))
    if zoom:
        plt.xlim(400, 500)
        plt.ylim(0, 2000)
#    plt.show()
    plt.savefig('figs/pu_in_fabs{}.png'.format('' if not zoom else '_zoom'))

def plot_mass_in_repos(protos, args):
    plt.clf()
    plt.plot(*args)
    plt.title('Total Inventory of Material in Repositories')
    plt.ylabel('Mass (kg)')
    plt.xlabel('Timesteps (months)')
    plt.legend(list(protos.keys()))
#    plt.show()
    plt.savefig('figs/mass_in_repos.png')

def plot_pu_in_repos(protos, args):
    plt.clf()
    plt.plot(*args)
    plt.ylabel('Mass of $^{239}Pu$ (kg)')
    plt.xlabel('Timesteps (months)')
    plt.legend(list(protos.keys()), loc='upper left')
    plt.tight_layout()
    plt.savefig('figs/pu_in_repos.png')

def plot_reciever_flow(receivers, args):
    plt.clf()
    plt.plot(*args)
    plt.legend(receivers.values()[0])
    plt.title('Flow of Commodities')
    plt.xlabel('Timesteps (months)')
#    plt.show()
    plt.savefig('figs/{}_flow.png'.format(receivers.keys()[0])) 

def invs():
    print('Inventories across Sims')
    rxtrs = {
        'base_case': ['reactor'],
        'military': ['reactor'],
        'tariff': ['reactor', 'b_reactor'],
        'outage': ['reactor'],
    }
    args = time_series(rxtrs, query_239)
    plot_pu_in_rxtrs(rxtrs, args)

    print("Repos")
    repos = {
        'base_case': ['repo'],
        'military': ['repo'],
        'outage': ['repo'],
        'tariff': ['repo', 'b_repo'],
    }
    args = time_series(repos, query_239)
    plot_pu_in_repos(repos, args)

def explore():   
    print("Rxtrs")
    rxtrs = {
        'base_case': ['reactor'],
        'military': ['reactor'],
        'tariff': ['reactor', 'b_reactor'],
        'outage': ['reactor'],
    }
    args = time_series(rxtrs, query_239)
    plot_pu_in_rxtrs(rxtrs, args)

    print("Fabs")
    fabs = {
        'base_case': ['fuelfab'],
        'military': ['fuelfab'],
        'tariff': ['fuelfab'],
        'outage': ['fuelfab'],
    }
    args = time_series(fabs, query_239)
    plot_pu_in_fabs(fabs, args, zoom=False)
    plot_pu_in_fabs(fabs, args, zoom=True)

    print("Repos")
    repos = {
        'base_case': ['repo'],
        'military': ['repo'],
        'outage': ['repo'],
        'tariff': ['repo', 'b_repo'],
    }
    args = time_series(repos, query_mass)
    plot_mass_in_repos(repos, args)
    args = time_series(repos, query_239)
    plot_pu_in_repos(repos, args)

def deployment():
    print('Rxtr Deployment')

    # data for individual and cumulative deployments
    x, y = time_series({"base_case": ["reactor"]}, query_built)
    args = []
    args += [x, np.cumsum(y)]
    args += [x[np.where(y > 0)], np.cumsum(y[np.where(y > 0)]), 'o']

    # plot
    plt.clf()
    plt.plot(*args)
    
    # words and formatting
    plt.ylabel('Number of Reactors')
    plt.xlabel('Timesteps (month)')
    plt.tight_layout()
    plt.savefig('figs/rxtr_deploy.png') 

def flows():
    print('flows out of producers')

    # data
    cases = ['base_case', 'military', 'tariff', 'outage']
    sources = {"mox": [["fuelfab", "mox"]], 
               "uox": [["b_uox", "b_uox"], 
                       ["enrichment", "uox"]]}
    for commod, query_args in sources.items():
        plt.clf()

        for case in cases:
            y = None
            for query_arg in query_args:
                if y is not None:
                    y += time_series({case: [query_arg]}, query_sender_flow)[1]
                else:
                    x, y = time_series({case: [query_arg]}, query_sender_flow)
            if case == 'base_case':
                plt.plot(x, np.cumsum(y), '--', zorder=10)
            else:
                plt.plot(x, np.cumsum(y))
            
        # plot
        plt.ylabel('{} Flow (kg)'.format(commod.upper()))
        plt.xlabel('Timesteps (month)')
        plt.legend(cases, loc='upper left')
        plt.tight_layout()
        plt.savefig('figs/{}_flow.png'.format(commod))

def tariff():
    print('Tariff BReactor Flows')
    
    # data
    recievers = {'b_reactor': ['uox', 'mox', 'b_uox']}
    args = []
    for proto, commods in recievers.items():
        for commod in commods:
            x, y = time_series({'tariff': [[proto, commod]]}, query_receiver_flow)
            # 12th timestep is last time a b_reactor gets a full core
            # (only show refuels, not initial cores)
            args += [x[11:], np.cumsum(y[11:])]

    # plotting
    plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    lines = ax.plot(*args)

    # point to tariff changes
    x, y = 150, 1.5e6
    ax.annotate('$t_0$', xy=(x, y - 5.5e5), xytext=(x, y + .1e6), 
                arrowprops=dict(width=2.5, headwidth=8))
    x, y = 300, 1.7e6
    ax.annotate('$t_1$', xy=(x, y - 5.5e5), xytext=(x, y + .1e6), 
                arrowprops=dict(width=2.5, headwidth=8))
    
    # wordsand layout
    ax.legend(recievers.values()[0])
    ax.set_xlabel('Timesteps (month)')
    ax.set_ylabel('Quantity (kg)')
    fig.tight_layout()

    fig.savefig('figs/tariff_b_reactor_flow.png') 

def outage():
    print('Outage Inventories')

    # data
    protos = ['fuelfab', 'separations', 'reactor']
    args1, args2, args3 = [], [], []
    zoomx, zoomy = 200, 400
    for proto in protos:
        args1 += time_series({'base_case': [proto]}, query_239)
        x, y = time_series({'outage': [proto]}, query_239)
        args2 += [x, y]
        args3 += [x[zoomx:zoomy], y[zoomx:zoomy]]

    # plotting
    plt.clf()
    fig = plt.figure()
    
    # # base case on top, outage on bottom
    # ax1 = plt.subplot2grid((2, 1), (0, 0))
    # ax1.plot(*args1)
    # ax1.set_xticklabels([])
    # ax2 = plt.subplot2grid((2, 1), (1, 0), sharey=ax1)
    # ax2.plot(*args2)

    # base case on top, outage on bottom, closeup on right    
    ax1 = plt.subplot2grid((2, 3), (0, 0), colspan=2)
    ax1.plot(*args1)
    ax1.set_xticklabels([])
    ax2 = plt.subplot2grid((2, 3), (1, 0), colspan=2, sharey=ax1)
    ax2.plot(*args2)
    ax3 = plt.subplot2grid((2, 3), (0, 2), rowspan=2)
    ax3.plot(*args3)
    ticks = [5000 * x for x in range(1, 5)]
    ax3.set_yticklabels([])

    # words and layout
    ax1.legend(protos, loc='upper left')
    fig.text(0.015, 0.65, 'Mass of $^{239}Pu$ (kg)', rotation='vertical')
    fig.text(0.45, 0.015, 'Timesteps (month)')    
    fig.tight_layout()
    fig.subplots_adjust(left=0.13, bottom=0.09)

    fig.savefig('figs/outage_invs.png') 

if __name__ == "__main__":
    print("Postprocessing dbs")
    dbs = ['base_case', 'military', 'tariff', 'outage', 'once_through']
    post_dbs(dbs)

    plt.style.use('ggplot')
    
    explore()
    deployment()
    invs()
    tariff()           
    outage()
    flows()
