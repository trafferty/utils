#!/usr/bin/env python

import subprocess as p
import argparse
import sys
from textwrap import dedent

def divergence(branch_a, branch_b):
    merge_base = p.check_output(['git', 'merge-base', branch_a, branch_b]).strip()
    branch_a_commits = p.check_output(['git', 'log', '--oneline',
                                       merge_base + '..' + branch_a]).splitlines()
    branch_b_commits = p.check_output(['git', 'log', '--oneline',
                                       merge_base + '..' + branch_b]).splitlines()
    return branch_a_commits, branch_b_commits, merge_base

def commits_between(branch_a, branch_b):
    return divergence(branch_a, branch_b)[:2]

def distance(branch_a, branch_b):
    return sum(map(len, commits_between(branch_a, branch_b)))

def base_date(branch_a, branch_b):
    _, _, base = divergence(branch_a, branch_b)
    full_date = p.check_output(['git', 'show', '--format=format:%ad', base]).splitlines()[0]
    relative_date = p.check_output(['git', 'show', '--format=format:%ar', base]).splitlines()[0]
    return '%s (%s)' %(relative_date, full_date)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Branch metrics')
    parser.add_argument('branches', type=str, nargs=2, metavar='branch',
                        help='branches to compare metrics')
    parser.add_argument('-a', '--all', dest='all', action='store_true',
                        help='show all the changes')
    parser.add_argument('-d', '--distance', dest='distance', action='store_true',
                        help='show only "distance" statistic')
    args = parser.parse_args()
    try:
        ba, bb = args.branches
        if args.distance:
            print( distance(ba, bb))
            sys.exit(0)
        a, b = commits_between(ba, bb)
        s = sorted([(len(a), ba), (len(b), bb)])
        print (dedent("""
        Distance report:

             o %s
              \ <--------- %d commits
               \ 
                \   o %s
                 \ / <---- %d commits
                  o
                  %s
        """ %(s[1][1], s[1][0], s[0][1], s[0][0],
              base_date(ba, bb))))
        if len(a) * len(b) == 0:
            print( 'This is a fast-forward. Merge with no fear!')
        print( 'Total distance:', len(a)+len(b), 'commits')
        if args.all:
            if len(a):
                print('\nCommit description in branch %s (and NOT in branch %s):' %(ba, bb))
                print('  ' + '\n  '.join(a))
            if len(b):
                print('\nCommit description in branch %s (and NOT in branch %s):' %(bb, ba))
                print('  ' + '\n  '.join(b))

    except p.CalledProcessError as err:
        print ('git failed with return code', err.returncode)
        sys.exit(1)
