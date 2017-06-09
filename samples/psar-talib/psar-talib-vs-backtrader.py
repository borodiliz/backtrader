#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2017 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import argparse
import datetime

import backtrader as bt


class St(bt.Strategy):
    params = dict(

                  talib=False
                  )

    def __init__(self):

        if self.p.talib:
            self.psar0 = bt.talib.SAR(self.datas[0].high, self.datas[0].low)
        else:
            self.psar0 = bt.ind.PSAR(self.datas[0])

        try:
            if self.p.talib:
                self.psar1 = bt.talib.SAR(self.datas[1].high, self.datas[1].low)
            else:
                self.psar1 = bt.ind.PSAR(self.datas[1])
        except IndexError:
            False #Nothing to do

        try:
            if self.p.talib:
                self.psar2 = bt.talib.SAR(self.datas[2].high, self.datas[2].low)
            else:
                self.psar2 = bt.ind.PSAR(self.datas[2])
        except IndexError:
            False #Nothing to do
        pass

    def next(self):
        #Date,Time,Open,High,Low,Close,Volume,OpenInterest
        txt = []

        txt.append(self.data0.datetime.datetime().strftime('%Y-%m-%d,%H:%M:%S'))
        txt.append(self.data0.open[0])
        txt.append(self.data0.high[0])
        txt.append(self.data0.low[0])
        txt.append(self.data0.close[0])
        txt.append(self.data0.volume[0])
        txt.append(self.data0.openinterest[0])



        #        txt.append('{:04d}'.format(len(self)))
        #        txt.append('{:04d}'.format(len(self.data0)))
        #        txt.append(self.data0.datetime.datetime())
        #        txt.append('{:.2f}'.format(self.data0.close[0]))
        #        txt.append('PSAR')
        #        txt.append('{:04.2f}'.format(self.psar0[0]))
        try:
            if len(self.datas[1]):
                txt.append('{:04d}'.format(len(self.data1)))
                txt.append(self.data1.datetime.datetime())
                txt.append('{:.2f}'.format(self.data1.close[0]))
                txt.append('PSAR')
                txt.append('{:04.2f}'.format(self.psar1[0]))
        except IndexError:
            False #Nothing to do

        try:
            if len(self.datas[2]):
                txt.append('{:04d}'.format(len(self.data2)))
                txt.append(self.data2.datetime.datetime())
                txt.append('{:.2f}'.format(self.data2.close[0]))
                txt.append('PSAR')
                txt.append('{:04.2f}'.format(self.psar2[0]))
        except IndexError:
            False #Nothing to do

        print(','.join(str(x) for x in txt))


def runstrat(args=None):
    args = parse_args(args)

    cerebro = bt.Cerebro()

    # Data feed kwargs
    kwargs = dict(
                  timeframe=bt.TimeFrame.Minutes,
                  compression=5,
                  )

    # Parse from/to-date
    dtfmt, tmfmt = '%Y-%m-%d', 'T%H:%M:%S'
    for a, d in ((getattr(args, x), x) for x in ['fromdate', 'todate']):
        if a:
            strpfmt = dtfmt + tmfmt * ('T' in a)
            kwargs[d] = datetime.datetime.strptime(a, strpfmt)

    # Data feed
    data0 = bt.feeds.BacktraderCSVData(dataname=args.data0, timeframe=bt.TimeFrame.Minutes, compression=args.compression)

    if args.adddata:
        cerebro.adddata(data0)

    if args.addresample10m:
        cerebro.resampledata(data0, timeframe=bt.TimeFrame.Minutes, compression=10)

    if args.addresample60m:
        cerebro.resampledata(data0, timeframe=bt.TimeFrame.Minutes, compression=60)

    # Broker
    cerebro.broker = bt.brokers.BackBroker(** eval('dict(' + args.broker + ')'))

    # Sizer
    cerebro.addsizer(bt.sizers.FixedSize, ** eval('dict(' + args.sizer + ')'))

    # Strategy
    cerebro.addstrategy(St, ** eval('dict(' + args.strat + ')'))

    # Execute
    cerebro.run(** eval('dict(' + args.cerebro + ')'))

    if args.plot:  # Plot if requested to
        cerebro.plot(** eval('dict(' + args.plot + ')'))


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=(
                                     'Sample Skeleton'
                                     )
                                     )

    parser.add_argument('--data0', default='../../datas//2006-min-005.txt',
                        required=False, help='Data to read in')

    # Defaults for dates
    parser.add_argument('--fromdate', required=False, default='',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--todate', required=False, default='',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--cerebro', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--broker', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--sizer', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--strat', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--plot', required=False, default='',
                        nargs='?', const='{}',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--adddata', action='store_true', required=False,
                        help='Add data')

    parser.add_argument('--addresample10m', action='store_true', required=False,
                        help='Add resample for 10 minute data')

    parser.add_argument('--addresample60m', action='store_true', required=False,
                        help='Add resample for 15 minute data')

    parser.add_argument('--compression', required=False, default=5, type=int,
                        help='Compression for data0')

    return parser.parse_args(pargs)


if __name__ == '__main__':
    runstrat()
