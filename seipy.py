#
# This work is licensed under the Creative Commons Attribution 3.0 Unported License. To view a copy of this license,
# visit http://creativecommons.org/licenses/by/3.0/ or send a letter to
# Creative Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.
#

import optparse
# pylab can be a bit tricky to install.  I needed NumPy and Matplotlib.
# Try looking at http://www.annedawson.net/pylab.html for directions.
import pylab

# Here's how to get the input data set:
# Go to http://www.iris.edu/SeismiQuery/sq-events.htm and put in the
# relevant parameters.  It will take you to a 2nd page.
# Follow the directions to download a WEED Event File
# (Windows Extracted from Event Data) that is a result of the database query.
# As far as the format of this text file, it's best to look at the table you get after the
# query, then match up the columns with the textual data.  There are no
# headers in the WEED Event File, but there are headers in the web page table that you can refer to.
#
# The parameters I used for the query are:
# mag : >= 6
# time 1900 to today (unfortunately they only seem to go back to 1960/01/30)
# everything else is default
#
# Here's what it gives me on the 2nd page:
# Event selection criteria:primary:starttime 08/19/1900:endtime 09/19/2011:magnitude >= 6:order by time desc
# Your query returned 4619 events, 4619 origins, and 6516 magnitudes.
#


class SeismicHistogram():
    def __init__(self, filepath):
        self.filepath = filepath
        self.verbose = False
        self.plot_interactive = False

    def set_verbose(self, verbose = True):
        self.verbose = verbose

    def set_plot_interactive(self, plot_interactive = True):
        self.plot_interactive = plot_interactive

    # Essentially initialization.
    # Read the input file for various runtime values such as year and magnitude limits
    def setup(self):
        # get start and end years and lowest and highest mag from the file
        self.start_year = -1
        self.end_year = -1
        self.low_mag = -1
        self.high_mag = -1
        seismic_file = open(self.filepath)
        self.seismic_data = seismic_file.readlines()
        seismic_file.close()
        for line in self.seismic_data:
            if len(line) > 1:
                year = self.get_year_from_line(line)
                mag = self.get_mag_from_line(line)
                if year is not None:
                    if (self.start_year < 0) or (self.start_year > year):
                        self.start_year = year
                    if (self.end_year < 0) or (self.end_year < year):
                        self.end_year = year
                    if (self.low_mag < 0) or (self.low_mag > mag):
                        self.low_mag = mag
                    if (self.high_mag < 0) or (self.high_mag < mag):
                        self.high_mag = mag
        self.low_mag = int(self.low_mag)
        self.high_mag = int(self.high_mag)
        if self.verbose:
            print self.start_year, self.end_year, self.low_mag, self.high_mag

    def run(self, save_to_file = False):
        if self.verbose:
            print self.filepath
        self.setup()
        self.mag = self.low_mag
        while self.mag <= self.high_mag:
            if self.verbose:
                print self.mag

            # init histogram to all 0 counts
            self.seismic_histogram = {}
            year = self.start_year
            while year <= self.end_year:
                self.seismic_histogram[year] = 0
                year += 1

            # read in seismic data
            seismic_file = open(self.filepath)
            self.seismic_data = seismic_file.readlines()
            seismic_file.close()

            # create the histogram
            for line in self.seismic_data:
                line_list = line.strip().split(',')
                if len(line_list) > 1:
                    int_year = int(self.get_year_from_line(line))
                    int_mag = int(self.get_mag_from_line(line))
                    if int_mag >= self.mag:
                        self.seismic_histogram[int_year] += 1

            self.plot()
            self.mag += 1

    def get_year_from_line(self, line):
        line_list = line.strip().split(',')
        if len(line_list) < 1:
            year_val = None
        else:
            date = line_list[1].strip()
            year = date.split('/')[0]
            year_val = int(year)
        return year_val

    def get_mag_from_line(self, line):
        line_list = line.strip().split(',')
        if len(line_list) < 1:
            mag_val = None
        else:
            # mag is last entry in line
            mag_val = float(line_list[-1].strip())
        return mag_val

    def plot(self):
        # convert the dict to a set of 2 lists for plotting
        y_list = []
        x_list = []
        for y in self.seismic_histogram:
            y_list.append(self.seismic_histogram[y])
            x_list.append(y)
        pylab.plot(x_list, y_list, linewidth=2.0)
        pylab.xlabel('year')
        pylab.ylabel('count')
        pylab.title('seismic activity per year >= ' + str(self.mag) + " magnitude")
        pylab.grid(True)
        if self.plot_interactive:
            pylab.show()
        else:
            pylab.savefig("seismic_" + str(self.mag) + ".png")
        pylab.close()


if __name__ == '__main__':
    # default filename
    filepath = "weedevent-new.txt"

    # allow the user to specify the filename
    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", dest="filepath",
                      help="read seismic data from this file", metavar="file")
    parser.add_option("-v", "--verbose", action="store_true", default = False,
                      help="print messages to aid in debug")
    parser.add_option("-i", "--interactive", action="store_true", default = False,
                      help="plot the graph interactively (instead of writing plot to a file)")
    (options, args) = parser.parse_args()
    if options.filepath is not None:
        filepath = options.filepath

    hist = SeismicHistogram(filepath)
    if options.verbose:
        hist.set_verbose()
    if options.interactive:
        hist.set_plot_interactive()
    hist.run(True)
