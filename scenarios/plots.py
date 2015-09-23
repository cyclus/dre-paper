#!/usr/bin/env python

import subprocess

import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style

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

def post_dbs(dbs):
    for name in dbs:
        cmd = "cyan -db {}.sqlite post".format(name)
        subprocess.call(cmd.split(), shell=False)

def time_series(protos, query):
    args = []
    for name, kinds in protos.items():
        con = sql.connect('{}.sqlite'.format(name))
        cur = con.cursor()
        
        info = cur.execute('SELECT * from INFO').fetchall()
        simid = info[0][0]
        
        x, y = None, None
        for kind in kinds:
            data = np.array(cur.execute(query, [simid, kind, simid]).fetchall())
            x = data[:, 0] if x is None else x
            if y is not None:
                y += data[:, 1]
            else:
                y = data[:, 1]
        args.extend([x, y])
    return args    

def plot_pu_in_rxtrs(protos, args):
    plt.clf()
    plt.plot(*args)
    plt.title('Inventory of $^{239}Pu$ in All Reactors')
    plt.ylabel('Mass (kg)')
    plt.xlabel('Timesteps (months)')
    plt.legend(list(protos.keys()))
#    plt.show()
    plt.savefig('figs/pu_in_rxtrs.png')

def plot_pu_in_fabs(protos, args):
    plt.clf()
    plt.plot(*args)
    plt.title('Inventory of $^{239}Pu$ in Recycled-Fuel Fabrication Facilities')
    plt.ylabel('Mass (kg)')
    plt.xlabel('Timesteps (months)')
    plt.legend(list(protos.keys()))
#    plt.show()
    plt.savefig('figs/pu_in_fabs.png')

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
    plt.title('Inventory of $^{239}Pu$ in Repositories')
    plt.ylabel('Mass (kg)')
    plt.xlabel('Timesteps (months)')
    plt.legend(list(protos.keys()))
#    plt.show()
    plt.savefig('figs/pu_in_repos.png')

def plot_base_rxtr_deployment(args):
    plt.clf()
    plt.plot(*args)
    plt.title('Number of Reators')
    plt.xlabel('Timesteps (months)')
    plt.ylim(0, 30)
#    plt.show()
    plt.savefig('figs/base_rxtr_deploy.png') 

def primary():   
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
    plot_pu_in_fabs(fabs, args)

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

    args = time_series({"base_case": ["reactor"]}, query_built)
    args[1] = np.cumsum(args[1])
    plot_base_rxtr_deployment(args)



if __name__ == "__main__":
    print("Postprocessing dbs")
    dbs = ['base_case', 'military', 'tariff', 'outage']
    post_dbs(dbs)

    style.use('bmh')
    
    primary()
