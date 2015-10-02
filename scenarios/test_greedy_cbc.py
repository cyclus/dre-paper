#!/usr/bin/env python

import subprocess

import sqlite3 as sql
import numpy as np

from plots import post_dbs

query_receiver_flow = """SELECT TOTAL(sub.qty) AS Quantity
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

query_sender_flow = """SELECT TOTAL(sub.qty) AS Quantity
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

def flow(db, commod, proto):
    con = sql.connect(db)
    cur = con.cursor()
    info = cur.execute('SELECT * from INFO').fetchall()
    simid = info[0][0]
    args = [simid, proto, commod, simid]
    data = np.array(cur.execute(query_receiver_flow, args).fetchall())
    con.close()
    return data

def post_dbs(dbs):
    for name in dbs:
        cmd = "cyan -db {} post".format(name)
        subprocess.call(cmd.split(), shell=False)

# cases = "base_case once_through military tariff outage"

msg = """Case: {}, Commod: {}, Proto: {}
Different at t={}
Greedy vals: {}
Cbc vals:    {}
"""

def test(cases, commods, protos):
    for case in cases.split():
        print('Testing {}'.format(case))
        for commod in commods.split():
            for proto in protos.split():
                gdb = "{}.sqlite".format(case) 
                cdb = "{}_cbc.sqlite".format(case)
                post_dbs([gdb, cdb])
                greedy = flow(gdb, commod, proto)
                cbc = flow(cdb, commod, proto)
                if not np.allclose(greedy, cbc):
                    times = np.where(np.abs(greedy - cbc) > 1e-2)[0]
                    print(msg.format(case, commod, proto, 
                                     times,
                                     greedy[times].flatten(), 
                                     cbc[times].flatten()))

def main():
    cases = "once_through base_case outage military tariff"

    print ""
    print "-" * 20
    print "Testing cases: " + cases
    print "-" * 20
    print ""
    
    commods = "uox mox mil_mox b_uox"
    protos = "reactor b_reactor"
    test(cases, commods, protos)

    print ""
    print "-" * 20
    print "Reactor Testing Complete"
    print "-" * 20
    print ""

    commods = "uox mox spent_uox spent_mox natl_u depleted_u sep_stream waste mil_mox b_uox"
    protos = "enrichment reactor separations fuelfab repo b_reactor"
    # test(cases, commods, protos)


if __name__ == "__main__":
    main()
