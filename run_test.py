#!/usr/bin/env python3

""" Tests for running the engine """

# Import code to be tested
import run

# Import needed packages
import unittest
import numpy
import scipy.stats as ss
import copy

# Define sample measure for use in all tests below
sample_measure = {"name": "sample measure 1",
                  "active": 1,
                  "market_entry_year": None,
                  "market_exit_year": None,
                  "end_use": {"primary": ["heating", "cooling"],
                              "secondary": None},
                  "fuel_type": {"primary": "electricity (grid)",
                                "secondary": None},
                  "technology_type": {"primary": "supply",
                                      "secondary": None},
                  "technology": {"primary": ["boiler (electric)",
                                 "ASHP", "GSHP", "room AC"],
                                 "secondary": None},
                  "bldg_type": "single family home",
                  "structure_type": ["new", "existing"],
                  "climate_zone": ["AIA_CZ1", "AIA_CZ2"]}

# Define sample measure w/ secondary msegs for use in all tests below
sample_measure2 = {"name": "sample measure 1",
                   "active": 1,
                   "market_entry_year": None,
                   "market_exit_year": None,
                   "end_use": {"primary": ["heating", "cooling"],
                               "secondary": "lighting"},
                   "fuel_type": {"primary": "electricity (grid)",
                                 "secondary": "electricity (grid)"},
                   "technology_type": {"primary": "supply",
                                       "secondary": "supply"},
                   "technology": {"primary": ["boiler (electric)",
                                  "ASHP", "GSHP", "room AC"],
                                  "secondary": "general service (LED)"},
                   "structure_type": ["new", "existing"],
                   "bldg_type": "single family home",
                   "climate_zone": ["AIA_CZ1", "AIA_CZ2"]}


class CommonMethods(object):
    """ Define common methods for use in all tests below """

    # Create a routine for checking equality of a dict with point vals
    def dict_check(self, dict1, dict2, msg=None):
        for (k, i), (k2, i2) in zip(sorted(dict1.items()),
                                    sorted(dict2.items())):
            if isinstance(i, dict):
                self.assertCountEqual(i, i2)
                self.dict_check(i, i2)
            else:
                self.assertAlmostEqual(dict1[k], dict2[k2], places=2)

    # Create a routine for checking equality of a dict with list vals
    def dict_check_list(self, dict1, dict2, msg=None):
        for (k, i), (k2, i2) in zip(sorted(dict1.items()),
                                    sorted(dict2.items())):
            if isinstance(i, dict):
                self.assertCountEqual(i, i2)
                self.dict_check_list(i, i2)
            else:
                # Expect numpy arrays and/or point values
                if (type(i) != int and type(i) != float):
                    numpy.testing.assert_array_almost_equal(
                        i, i2, decimal=2)
                else:
                    self.assertAlmostEqual(dict1[k], dict2[k2],
                                           places=2)


class TestMeasureInit(unittest.TestCase):
    """ Ensure that measure attributes are correctly initiated """

    def test_attributes(self):
        # Create an instance of the object using sample_measure
        measure_instance = run.Measure(**sample_measure)
        # Put object attributes into a dict
        attribute_dict = measure_instance.__dict__
        # Loop through sample measure keys and compare key values
        # to those from the "attribute_dict"
        for key in sample_measure.keys():
            self.assertEqual(attribute_dict[key],
                             sample_measure[key])


class AddKeyValsTest(unittest.TestCase, CommonMethods):
    """ Test the operation of the add_keyvals function to verify it
    adds together dict items correctly """

    # Create a measure instance to use in the testing
    measure_instance = run.Measure(**sample_measure)

    # 1st dict to be entered into the "ok" test of the function
    base_dict1 = {"level 1a":
                  {"level 2aa":
                      {"2009": 2, "2010": 3},
                   "level2ab":
                      {"2009": 4, "2010": 5}},
                  "level 1b":
                  {"level 2ba":
                      {"2009": 6, "2010": 7},
                   "level2bb":
                      {"2009": 8, "2010": 9}}}

    # 1st dict to be entered into the "fail" test of the function
    base_dict2 = copy.deepcopy(base_dict1)

    # 2nd dict to be added to "base_dict1" in the "ok" test of the function
    ok_add_dict2 = {"level 1a":
                    {"level 2aa":
                        {"2009": 2, "2010": 3},
                     "level2ab":
                        {"2009": 4, "2010": 5}},
                    "level 1b":
                    {"level 2ba":
                        {"2009": 6, "2010": 7},
                     "level2bb":
                        {"2009": 8, "2010": 9}}}

    # 2nd dict to be added to "base_dict2" in the "fail" test of the function
    fail_add_dict2 = {"level 1a":
                      {"level 2aa":
                          {"2009": 2, "2010": 3},
                       "level2ab":
                          {"2009": 4, "2010": 5}},
                      "level 1b":
                      {"level 2ba":
                          {"2009": 6, "2010": 7},
                       "level2bb":
                          {"2009": 8, "2011": 9}}}

    # Correct output of the "ok" test to check against
    ok_out = {"level 1a":
              {"level 2aa":
                  {"2009": 4, "2010": 6},
               "level2ab":
                  {"2009": 8, "2010": 10}},
              "level 1b":
              {"level 2ba":
                  {"2009": 12, "2010": 14},
               "level2bb":
                  {"2009": 16, "2010": 18}}}

    # Test the "ok" function output
    def test_ok_add(self):
        dict1 = self.measure_instance.add_keyvals(self.base_dict1,
                                                  self.ok_add_dict2)
        dict2 = self.ok_out
        self.dict_check(dict1, dict2)

    # Test the "fail" function output
    def test_fail_add(self):
        with self.assertRaises(KeyError):
            self.measure_instance.add_keyvals(self.base_dict2,
                                              self.fail_add_dict2)


class ReduceSqftStockCostTest(unittest.TestCase, CommonMethods):
    """ Test the operation of the reduce_sqft function to verify
    that it properly divides dict key values by a given factor (used in special
    case where square footage is used as the microsegment stock) """

    # Create a measure instance to use in the testing
    measure_instance = run.Measure(**sample_measure)

    # Initialize a factor to divide input dict key values by
    test_factor = 4

    # Base input dict to be divided by test_factor in "ok" test
    base_dict = {"stock":
                 {"total":
                     {"2009": 100, "2010": 200},
                  "competed":
                      {"2009": 300, "2010": 400}},
                 "energy":
                 {"total":
                     {"2009": 500, "2010": 600},
                  "competed":
                     {"2009": 700, "2010": 800},
                  "efficient":
                     {"2009": 700, "2010": 800}},
                 "carbon":
                 {"total":
                     {"2009": 500, "2010": 600},
                  "competed":
                     {"2009": 700, "2010": 800},
                  "efficient":
                     {"2009": 700, "2010": 800}},
                 "cost":
                 {"baseline": {
                     "stock": {"2009": 900, "2010": 1000},
                     "energy": {"2009": 900, "2010": 1000},
                     "carbon": {"2009": 900, "2010": 1000}},
                  "measure": {
                     "stock": {"2009": 1100, "2010": 1200},
                     "energy": {"2009": 1100, "2010": 1200},
                     "carbon": {"2009": 1100, "2010": 1200}}}}

    # Correct output of the "ok" test to check against
    ok_out = {"stock":
              {"total":
                  {"2009": 25, "2010": 50},
               "competed":
                   {"2009": 75, "2010": 100}},
              "energy":
              {"total":
                  {"2009": 500, "2010": 600},
               "competed":
                  {"2009": 700, "2010": 800},
               "efficient":
                  {"2009": 700, "2010": 800}},
              "carbon":
              {"total":
                   {"2009": 500, "2010": 600},
               "competed":
                   {"2009": 700, "2010": 800},
               "efficient":
                   {"2009": 700, "2010": 800}},
              "cost":
              {"baseline": {
                  "stock": {"2009": 225, "2010": 250},
                  "energy": {"2009": 900, "2010": 1000},
                  "carbon": {"2009": 900, "2010": 1000}},
               "measure": {
                  "stock": {"2009": 275, "2010": 300},
                  "energy": {"2009": 1100, "2010": 1200},
                  "carbon": {"2009": 1100, "2010": 1200}}}}

    # Test the "ok" function output
    def test_ok_add(self):
        dict1 = self.measure_instance.reduce_sqft(self.base_dict,
                                                  self.test_factor)
        dict2 = self.ok_out
        self.dict_check(dict1, dict2)


# NOT SURE WE NEED THIS TEST

# class RandomSampleTest(unittest.TestCase):
#     """ Test that the "rand_list_gen" yields an output
#     list of sampled values that are correctly distributed """

#     # Create a measure instance to use in the testing
#     measure_instance = run.Measure(**sample_measure)

#     # Set test sampling number
#     test_sample_n = 100

#     # Set of input distribution information that should
#     # yield valid outputs
#     test_ok_in = [["normal", 10, 2], ["weibull", 5, 8],
#                   ["triangular", 3, 7, 10]]

#     # Set of input distribution information that should
#     # yield value errors
#     test_fail_in = [[1, 10, 2], ["triangle", 5, 8, 10],
#                     ["triangular", 3, 7]]

#     # Calls to the scipy fit function that will be used
#     # to check for correct fitted distribution parameters
#     # for sampled values
#     test_fit_calls = ['ss.norm.fit(sample)',
#                       'ss.weibull_min.fit(sample, floc = 0)',
#                       'ss.triang.fit(sample)']

#     # Correct set of outputs for given random sampling seed
#     test_outputs = [numpy.array([10.06, 2.03]),
#                     numpy.array([4.93, 0, 8.02]),
#                     numpy.array([0.51, 3.01, 7.25])]

#     # Test for correct output from "ok" input distribution info.
#     def test_distrib_ok(self):
#         # Seed random number generator to yield repeatable results
#         numpy.random.seed(5423)
#         for idx in range(0, len(self.test_ok_in)):
#             # Sample values based on distribution input info.
#             sample = self.measure_instance.rand_list_gen(self.test_ok_in[idx],
#                                                          self.test_sample_n)
#             # Fit parameters for sampled values and check against
#             # known correct parameter values in "test_outputs" * NOTE:
#             # this adds ~ 0.15 s to test computation
#             for elem in range(0, len(self.test_outputs[idx])):
#                 with numpy.errstate(divide='ignore'):  # Warning for triang
#                     self.assertAlmostEqual(
#                         list(eval(self.test_fit_calls[idx]))[elem],
#                         self.test_outputs[idx][elem], 2)

#     # Test for correct output from "fail" input distribution info.
#     def test_distrib_fail(self):
#         for idx in range(0, len(self.test_fail_in)):
#             with self.assertRaises(ValueError):
#                 self.measure_instance.rand_list_gen(
#                     self.test_fail_in[idx], self.test_sample_n)

class CreateKeyChainTest(unittest.TestCase, CommonMethods):
    """ Test the operation of the create_keychain function to verify that
    it yields proper key chain output given input microsegment information """

    # Create a measure instance to use in the testing
    measure_instance = run.Measure(**sample_measure2)

    # Correct key chain output (primary microsegment)
    ok_out_primary = [('primary', 'AIA_CZ1', 'single family home',
                       'electricity (grid)', 'heating', 'supply',
                       'boiler (electric)'),
                      ('primary', 'AIA_CZ1', 'single family home',
                       'electricity (grid)', 'heating', 'supply', 'ASHP'),
                      ('primary', 'AIA_CZ1', 'single family home',
                       'electricity (grid)', 'heating', 'supply', 'GSHP'),
                      ('primary', 'AIA_CZ1', 'single family home',
                       'electricity (grid)', 'heating', 'supply', 'room AC'),
                      ('primary', 'AIA_CZ1', 'single family home',
                       'electricity (grid)', 'cooling', 'supply',
                       'boiler (electric)'),
                      ('primary', 'AIA_CZ1', 'single family home',
                       'electricity (grid)', 'cooling', 'supply', 'ASHP'),
                      ('primary', 'AIA_CZ1', 'single family home',
                       'electricity (grid)', 'cooling', 'supply', 'GSHP'),
                      ('primary', 'AIA_CZ1', 'single family home',
                       'electricity (grid)', 'cooling', 'supply', 'room AC'),
                      ('primary', 'AIA_CZ2', 'single family home',
                       'electricity (grid)', 'heating', 'supply',
                       'boiler (electric)'),
                      ('primary', 'AIA_CZ2', 'single family home',
                       'electricity (grid)', 'heating', 'supply', 'ASHP'),
                      ('primary', 'AIA_CZ2', 'single family home',
                       'electricity (grid)', 'heating', 'supply', 'GSHP'),
                      ('primary', 'AIA_CZ2', 'single family home',
                       'electricity (grid)', 'heating', 'supply', 'room AC'),
                      ('primary', 'AIA_CZ2', 'single family home',
                       'electricity (grid)', 'cooling', 'supply',
                       'boiler (electric)'),
                      ('primary', 'AIA_CZ2', 'single family home',
                       'electricity (grid)', 'cooling', 'supply', 'ASHP'),
                      ('primary', 'AIA_CZ2', 'single family home',
                       'electricity (grid)', 'cooling', 'supply', 'GSHP'),
                      ('primary', 'AIA_CZ2', 'single family home',
                       'electricity (grid)', 'cooling', 'supply', 'room AC')]

    # Correct key chain output (secondary microsegment)
    ok_out_secondary = [('secondary', 'AIA_CZ1', 'single family home',
                         'electricity (grid)', 'lighting',
                         'general service (LED)'),
                        ('secondary', 'AIA_CZ2', 'single family home',
                         'electricity (grid)', 'lighting',
                         'general service (LED)')]

    # Test the generation of a list of primary mseg key chains
    def test_primary(self):
        self.assertEqual(
            self.measure_instance.create_keychain("primary")[0],
            self.ok_out_primary)

    # Test the generation of a list of secondary mseg key chains
    def test_secondary(self):
        self.assertEqual(
            self.measure_instance.create_keychain("secondary")[0],
            self.ok_out_secondary)


class PartitionMicrosegmentTest(unittest.TestCase, CommonMethods):
    """ Test the operation of the partition_microsegment function to verify
    that it properly partitions an input microsegment to yield the required
    competed stock/energy/cost and energy efficient consumption information """

    # Create a measure instance to use in the testing
    measure_instance = run.Measure(**sample_measure)

    # Set sample stock and energy inputs for testing
    test_stock = [{"2009": 100, "2010": 200, "2011": 300},
                  {"2025": 400, "2028": 500, "2035": 600},
                  {"2020": 700, "2021": 800, "2022": 900}]
    test_energy = [{"2009": 10, "2010": 20, "2011": 30},
                   {"2025": 40, "2028": 50, "2035": 60},
                   {"2020": 70, "2021": 80, "2022": 90}]
    test_carbon = [{"2009": 30, "2010": 60, "2011": 90},
                   {"2025": 120, "2028": 150, "2035": 180},
                   {"2020": 210, "2021": 240, "2022": 270}]

    # Set sample base and measure costs to use in the testing
    test_base_cost = [{"2009": 10, "2010": 10, "2011": 10},
                      {"2025": 20, "2028": 20, "2035": 20},
                      {"2020": 30, "2021": 30, "2022": 30}]
    test_cost_meas = [20, 30, 40]

    # Set sample energy and carbon costs to use in the testing
    cost_energy = numpy.array((b'Test', 1, 2, 2, 2, 2, 2, 2, 2, 2),
                              dtype=[('Category', 'S11'), ('2009', '<f8'),
                                     ('2010', '<f8'), ('2011', '<f8'),
                                     ('2020', '<f8'), ('2021', '<f8'),
                                     ('2022', '<f8'), ('2025', '<f8'),
                                     ('2028', '<f8'), ('2035', '<f8')])
    cost_carbon = numpy.array((b'Test', 1, 4, 1, 1, 1, 1, 1, 1, 3),
                              dtype=[('Category', 'S11'), ('2009', '<f8'),
                                     ('2010', '<f8'), ('2011', '<f8'),
                                     ('2020', '<f8'), ('2021', '<f8'),
                                     ('2022', '<f8'), ('2025', '<f8'),
                                     ('2028', '<f8'), ('2035', '<f8')])

    # Set two alternative schemes to use in the testing,
    # where the first should yield a full list of outputs
    # and the second should yield a list with blank elements
    test_scheme = 'Technical potential'

    # Set a sample dict with information about stock turnover fractions
    # (new buildings)
    new_bldg_frac = [{"2009": 0.1, "2010": 0.05, "2011": 0.1},
                     {"2025": 0.1, "2028": 0.05, "2035": 0.1},
                     {"2020": 0.1, "2021": 0.95, "2022": 0.1}]

    # Set a relative performance list that should yield a
    # full list of valid outputs
    ok_relperf = [{"2009": 0.30, "2010": 0.30, "2011": 0.30},
                  {"2025": 0.15, "2028": 0.15, "2035": 0.15},
                  {"2020": 0.75, "2021": 0.75, "2022": 0.75}]

    # Set site-source conversion factors
    site_source_conv = numpy.array((b'Test', 1, 1, 1, 1, 1, 1, 1, 1, 1),
                                   dtype=[('Category', 'S11'), ('2009', '<f8'),
                                          ('2010', '<f8'), ('2011', '<f8'),
                                          ('2020', '<f8'), ('2021', '<f8'),
                                          ('2022', '<f8'), ('2025', '<f8'),
                                          ('2028', '<f8'), ('2035', '<f8')])

    # Set carbon intensity factors
    intensity_carb = numpy.array((b'Test', 3, 3, 3, 3, 3, 3, 3, 3, 3),
                                 dtype=[('Category', 'S11'), ('2009', '<f8'),
                                        ('2010', '<f8'), ('2011', '<f8'),
                                        ('2020', '<f8'), ('2021', '<f8'),
                                        ('2022', '<f8'), ('2025', '<f8'),
                                        ('2028', '<f8'), ('2035', '<f8')])

    # Set placeholder for technology diffusion parameters (currently blank)
    diffuse_params = None

    # Correct output of the "ok" function test
    ok_out = [[{"2009": 100, "2010": 200, "2011": 300},
               {"2009": 10, "2010": 20, "2011": 30},
               {"2009": 30, "2010": 60, "2011": 90},
               {"2009": 100, "2010": 200, "2011": 300},
               {"2009": 10, "2010": 20, "2011": 30},
               {"2009": 30, "2010": 60, "2011": 90},
               {"2009": 3, "2010": 6, "2011": 9},
               {"2009": 9, "2010": 18, "2011": 27},
               {"2009": 1000, "2010": 2000, "2011": 3000},
               {"2009": 10, "2010": 40, "2011": 60},
               {"2009": 30, "2010": 240, "2011": 90},
               {"2009": 1000, "2010": 2000, "2011": 3000},
               {"2009": 10, "2010": 40, "2011": 60},
               {"2009": 30, "2010": 240, "2011": 90},
               {"2009": 2000, "2010": 4000, "2011": 6000},
               {"2009": 3, "2010": 12, "2011": 18},
               {"2009": 9, "2010": 72, "2011": 27}],
              [{"2025": 400, "2028": 500, "2035": 600},
               {"2025": 40, "2028": 50, "2035": 60},
               {"2025": 120, "2028": 150, "2035": 180},
               {"2025": 400, "2028": 500, "2035": 600},
               {"2025": 40, "2028": 50, "2035": 60},
               {"2025": 120, "2028": 150, "2035": 180},
               {"2025": 6, "2028": 7.5, "2035": 9},
               {"2025": 18, "2028": 22.5, "2035": 27},
               {"2025": 8000, "2028": 10000, "2035": 12000},
               {"2025": 80, "2028": 100, "2035": 120},
               {"2025": 120, "2028": 150, "2035": 540},
               {"2025": 8000, "2028": 10000, "2035": 12000},
               {"2025": 80, "2028": 100, "2035": 120},
               {"2025": 120, "2028": 150, "2035": 540},
               {"2025": 12000, "2028": 15000, "2035": 18000},
               {"2025": 12, "2028": 15, "2035": 18},
               {"2025": 18, "2028": 22.5, "2035": 81}],
              [{"2020": 700, "2021": 800, "2022": 900},
               {"2020": 70, "2021": 80, "2022": 90},
               {"2020": 210, "2021": 240, "2022": 270},
               {"2020": 700, "2021": 800, "2022": 900},
               {"2020": 70, "2021": 80, "2022": 90},
               {"2020": 210, "2021": 240, "2022": 270},
               {"2020": 52.5, "2021": 60, "2022": 67.5},
               {"2020": 157.5, "2021": 180, "2022": 202.5},
               {"2020": 21000, "2021": 24000, "2022": 27000},
               {"2020": 140, "2021": 160, "2022": 180},
               {"2020": 210, "2021": 240, "2022": 270},
               {"2020": 21000, "2021": 24000, "2022": 27000},
               {"2020": 140, "2021": 160, "2022": 180},
               {"2020": 210, "2021": 240, "2022": 270},
               {"2020": 28000, "2021": 32000, "2022": 36000},
               {"2020": 105, "2021": 120, "2022": 135},
               {"2020": 157.5, "2021": 180, "2022": 202.5}]]

    # Test the "ok" function output
    def test_ok(self):
        for elem in range(0, len(self.test_stock)):
            lists1 = self.measure_instance.partition_microsegment(
                self.test_stock[elem],
                self.test_energy[elem],
                self.ok_relperf[elem],
                self.test_base_cost[elem],
                self.test_cost_meas[elem],
                self.cost_energy,
                self.cost_carbon,
                self.site_source_conv,
                self.intensity_carb,
                self.new_bldg_frac[elem],
                self.diffuse_params,
                self.test_scheme)

            lists2 = self.ok_out[elem]

            for elem2 in range(0, len(lists1)):
                self.dict_check(lists1[elem2], lists2[elem2])


class FindPartitionMasterMicrosegmentTest(unittest.TestCase, CommonMethods):
    """ Test the operation of the mseg_find_partition function to
    verify measure microsegment-related attribute inputs yield expected master
    microsegment output """

    # Sample input dict of microsegment performance/cost info. to reference in
    # generating and partitioning master microsegments for a measure
    sample_basein = {
        "AIA_CZ1": {
            "assembly": {
                "electricity (grid)": {
                    "heating": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 1, "2010": 1},
                                    "best": {"2009": 1, "2010": 1},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 1, "2010": 1},
                                    "best": {"2009": 1, "2010": 1},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 10, "2010": 10},
                                    "range": {"2009": 1, "2010": 1},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 20, "2010": 20},
                                    "range": {"2009": 2, "2010": 2},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "lights": {
                                "performance": {
                                    "typical": 0,
                                    "best": 0,
                                    "units": "NA",
                                    "source":
                                    "NA"},
                                "installed cost": {
                                    "typical": 0,
                                    "best": 0,
                                    "units": "NA",
                                    "source": "NA"},
                                "lifetime": {
                                    "average": 0,
                                    "range": 0,
                                    "units": "NA",
                                    "source": "NA"}}}},
                    "secondary heating": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 1, "2010": 1},
                                    "best": {"2009": 1, "2010": 1},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 1, "2010": 1},
                                    "best": {"2009": 1, "2010": 1},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 10, "2010": 10},
                                    "range": {"2009": 1, "2010": 1},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 20, "2010": 20},
                                    "range": {"2009": 2, "2010": 2},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "lights": {
                                "performance": {
                                    "typical": 0,
                                    "best": 0,
                                    "units": "NA",
                                    "source":
                                    "NA"},
                                "installed cost": {
                                    "typical": 0,
                                    "best": 0,
                                    "units": "NA",
                                    "source": "NA"},
                                "lifetime": {
                                    "average": 0,
                                    "range": 0,
                                    "units": "NA",
                                    "source": "NA"}}}},
                    "cooling": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 1, "2010": 1},
                                    "best": {"2009": 1, "2010": 1},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 1, "2010": 1},
                                    "best": {"2009": 1, "2010": 1},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 10, "2010": 10},
                                    "range": {"2009": 1, "2010": 1},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 20, "2010": 20},
                                    "range": {"2009": 2, "2010": 2},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "lights": {
                                "performance": {
                                    "typical": 0,
                                    "best": 0,
                                    "units": "NA",
                                    "source":
                                    "NA"},
                                "installed cost": {
                                    "typical": 0,
                                    "best": 0,
                                    "units": "NA",
                                    "source": "NA"},
                                "lifetime": {
                                    "average": 0,
                                    "range": 0,
                                    "units": "NA",
                                    "source": "NA"}}}},
                    "lighting": {
                        "commercial light type X": {
                            "performance": {
                                "typical": {"2009": 14, "2010": 14},
                                "best": {"2009": 14, "2010": 14},
                                "units": "lm/W",
                                "source":
                                "EIA AEO"},
                            "installed cost": {
                                "typical": {"2009": 14, "2010": 14},
                                "best": {"2009": 14, "2010": 14},
                                "units": "2014$/unit",
                                "source": "EIA AEO"},
                            "lifetime": {
                                "average": {"2009": 140, "2010": 140},
                                "range": {"2009": 14, "2010": 14},
                                "units": "years",
                                "source": "EIA AEO"}}}}},
            "single family home": {
                "electricity (grid)": {
                    "heating": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 1, "2010": 1},
                                    "best": {"2009": 1, "2010": 1},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 1, "2010": 1},
                                    "best": {"2009": 1, "2010": 1},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 10, "2010": 10},
                                    "range": {"2009": 1, "2010": 1},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 20, "2010": 20},
                                    "range": {"2009": 2, "2010": 2},
                                    "units": "years",
                                    "source": "EIA AEO"}}},
                        "supply": {
                            "boiler (electric)": {
                                "performance": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 20, "2010": 20},
                                    "range": {"2009": 2, "2010": 2},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "ASHP": {
                                "performance": {
                                    "typical": {"2009": 3, "2010": 3},
                                    "best": {"2009": 3, "2010": 3},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 3, "2010": 3},
                                    "best": {"2009": 3, "2010": 3},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 30, "2010": 30},
                                    "range": {"2009": 3, "2010": 3},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "GSHP": {
                                "performance": {
                                    "typical": {"2009": 4, "2010": 4},
                                    "best": {"2009": 4, "2010": 4},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 4, "2010": 4},
                                    "best": {"2009": 4, "2010": 4},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 40, "2010": 40},
                                    "range": {"2009": 4, "2010": 4},
                                    "units": "years",
                                    "source": "EIA AEO"}}}},
                    "secondary heating": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 5, "2010": 5},
                                    "best": {"2009": 5, "2010": 5},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 5, "2010": 5},
                                    "best": {"2009": 5, "2010": 5},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 50, "2010": 50},
                                    "range": {"2009": 5, "2010": 5},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 6, "2010": 6},
                                    "best": {"2009": 6, "2010": 6},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 6, "2010": 6},
                                    "best": {"2009": 6, "2010": 6},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 60, "2010": 60},
                                    "range": {"2009": 6, "2010": 6},
                                    "units": "years",
                                    "source": "EIA AEO"}}},
                        "supply": {
                            "non-specific": {
                                "performance": {
                                    "typical": {"2009": 7, "2010": 7},
                                    "best": {"2009": 7, "2010": 7},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 7, "2010": 7},
                                    "best": {"2009": 7, "2010": 7},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 70, "2010": 70},
                                    "range": {"2009": 7, "2010": 7},
                                    "units": "years",
                                    "source": "EIA AEO"}}}},
                    "cooling": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 8, "2010": 8},
                                    "best": {"2009": 8, "2010": 8},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 8, "2010": 8},
                                    "best": {"2009": 8, "2010": 8},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 80, "2010": 80},
                                    "range": {"2009": 8, "2010": 8},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 9, "2010": 9},
                                    "best": {"2009": 9, "2010": 9},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 9, "2010": 9},
                                    "best": {"2009": 9, "2010": 9},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 90, "2010": 90},
                                    "range": {"2009": 9, "2010": 9},
                                    "units": "years",
                                    "source": "EIA AEO"}}},
                        "supply": {
                            "central AC": {
                                "performance": {
                                    "typical": {"2009": 10, "2010": 10},
                                    "best": {"2009": 10, "2010": 10},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 10, "2010": 10},
                                    "best": {"2009": 10, "2010": 10},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 100, "2010": 100},
                                    "range": {"2009": 10, "2010": 10},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "room AC": {
                                "performance": {
                                    "typical": {"2009": 11, "2010": 11},
                                    "best": {"2009": 11, "2010": 11},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 11, "2010": 11},
                                    "best": {"2009": 11, "2010": 11},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 110, "2010": 110},
                                    "range": {"2009": 11, "2010": 11},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "ASHP": {
                                "performance": {
                                    "typical": {"2009": 12, "2010": 12},
                                    "best": {"2009": 12, "2010": 12},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 12, "2010": 12},
                                    "best": {"2009": 12, "2010": 12},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 120, "2010": 120},
                                    "range": {"2009": 12, "2010": 12},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "GSHP": {
                                "performance": {
                                    "typical": {"2009": 13, "2010": 13},
                                    "best": {"2009": 13, "2010": 13},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 13, "2010": 13},
                                    "best": {"2009": 13, "2010": 13},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 130, "2010": 130},
                                    "range": {"2009": 13, "2010": 13},
                                    "units": "years",
                                    "source": "EIA AEO"}}}},
                    "lighting": {
                        "linear fluorescent (LED)": {
                                "performance": {
                                    "typical": {"2009": 14, "2010": 14},
                                    "best": {"2009": 14, "2010": 14},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 14, "2010": 14},
                                    "best": {"2009": 14, "2010": 14},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 140, "2010": 140},
                                    "range": {"2009": 14, "2010": 14},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "general service (LED)": {
                                "performance": {
                                    "typical": {"2009": 15, "2010": 15},
                                    "best": {"2009": 15, "2010": 15},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 15, "2010": 15},
                                    "best": {"2009": 15, "2010": 15},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 150, "2010": 150},
                                    "range": {"2009": 15, "2010": 15},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "reflector (LED)": {
                                "performance": {
                                    "typical": {"2009": 16, "2010": 16},
                                    "best": {"2009": 16, "2010": 16},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 16, "2010": 16},
                                    "best": {"2009": 16, "2010": 16},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 160, "2010": 160},
                                    "range": {"2009": 16, "2010": 16},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "external (LED)": {
                                "performance": {
                                    "typical": {"2009": 17, "2010": 17},
                                    "best": {"2009": 17, "2010": 17},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 17, "2010": 17},
                                    "best": {"2009": 17, "2010": 17},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 170, "2010": 170},
                                    "range": {"2009": 17, "2010": 17},
                                    "units": "years",
                                    "source": "EIA AEO"}}}},
                "natural gas": {
                    "water heating": {
                        "performance": {
                            "typical": {"2009": 18, "2010": 18},
                            "best": {"2009": 18, "2010": 18},
                            "units": "EF",
                            "source":
                            "EIA AEO"},
                        "installed cost": {
                            "typical": {"2009": 18, "2010": 18},
                            "best": {"2009": 18, "2010": 18},
                            "units": "2014$/unit",
                            "source": "EIA AEO"},
                        "lifetime": {
                            "average": {"2009": 180, "2010": 180},
                            "range": {"2009": 18, "2010": 18},
                            "units": "years",
                            "source": "EIA AEO"}},
                    "heating": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 1, "2010": 1},
                                    "best": {"2009": 1, "2010": 1},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 1, "2010": 1},
                                    "best": {"2009": 1, "2010": 1},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 10, "2010": 10},
                                    "range": {"2009": 1, "2010": 1},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 20, "2010": 20},
                                    "range": {"2009": 2, "2010": 2},
                                    "units": "years",
                                    "source": "EIA AEO"}}}},
                    "secondary heating": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 5, "2010": 5},
                                    "best": {"2009": 5, "2010": 5},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 5, "2010": 5},
                                    "best": {"2009": 5, "2010": 5},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 50, "2010": 50},
                                    "range": {"2009": 5, "2010": 5},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 6, "2010": 6},
                                    "best": {"2009": 6, "2010": 6},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 6, "2010": 6},
                                    "best": {"2009": 6, "2010": 6},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 60, "2010": 60},
                                    "range": {"2009": 6, "2010": 6},
                                    "units": "years",
                                    "source": "EIA AEO"}}}},
                    "cooling": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 8, "2010": 8},
                                    "best": {"2009": 8, "2010": 8},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 8, "2010": 8},
                                    "best": {"2009": 8, "2010": 8},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 80, "2010": 80},
                                    "range": {"2009": 8, "2010": 8},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 9, "2010": 9},
                                    "best": {"2009": 9, "2010": 9},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 9, "2010": 9},
                                    "best": {"2009": 9, "2010": 9},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 90, "2010": 90},
                                    "range": {"2009": 9, "2010": 9},
                                    "units": "years",
                                    "source": "EIA AEO"}}}}}},
            "multi family home": {
                "electricity (grid)": {
                    "heating": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 19, "2010": 19},
                                    "best": {"2009": 19, "2010": 19},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 19, "2010": 19},
                                    "best": {"2009": 19, "2010": 19},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 190, "2010": 190},
                                    "range": {"2009": 19, "2010": 19},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 20, "2010": 20},
                                    "best": {"2009": 20, "2010": 20},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 20, "2010": 20},
                                    "best": {"2009": 20, "2010": 20},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 200, "2010": 200},
                                    "range": {"2009": 20, "2010": 20},
                                    "units": "years",
                                    "source": "EIA AEO"}}},
                        "supply": {
                            "boiler (electric)": {
                                "performance": {
                                    "typical": {"2009": 21, "2010": 21},
                                    "best": {"2009": 21, "2010": 21},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 21, "2010": 21},
                                    "best": {"2009": 21, "2010": 21},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 210, "2010": 210},
                                    "range": {"2009": 21, "2010": 21},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "ASHP": {
                                "performance": {
                                    "typical": {"2009": 22, "2010": 22},
                                    "best": {"2009": 22, "2010": 22},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 22, "2010": 22},
                                    "best": {"2009": 22, "2010": 22},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 220, "2010": 220},
                                    "range": {"2009": 22, "2010": 22},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "GSHP": {
                                "performance": {
                                    "typical": {"2009": 23, "2010": 23},
                                    "best": {"2009": 23, "2010": 23},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 23, "2010": 23},
                                    "best": {"2009": 23, "2010": 23},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 230, "2010": 230},
                                    "range": {"2009": 23, "2010": 23},
                                    "units": "years",
                                    "source": "EIA AEO"}}}},
                    "lighting": {
                        "linear fluorescent (LED)": {
                                "performance": {
                                    "typical": {"2009": 24, "2010": 24},
                                    "best": {"2009": 24, "2010": 24},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 24, "2010": 24},
                                    "best": {"2009": 24, "2010": 24},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 240, "2010": 240},
                                    "range": {"2009": 24, "2010": 24},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "general service (LED)": {
                                "performance": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 250, "2010": 250},
                                    "range": {"2009": 25, "2010": 25},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "reflector (LED)": {
                                "performance": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 250, "2010": 250},
                                    "range": {"2009": 25, "2010": 25},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "external (LED)": {
                                "performance": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 250, "2010": 250},
                                    "range": {"2009": 25, "2010": 25},
                                    "units": "years",
                                    "source": "EIA AEO"}}}}}},
        "AIA_CZ2": {
            "single family home": {
                "electricity (grid)": {
                    "heating": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 1, "2010": 1},
                                    "best": {"2009": 1, "2010": 1},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 1, "2010": 1},
                                    "best": {"2009": 1, "2010": 1},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 10, "2010": 10},
                                    "range": {"2009": 1, "2010": 1},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 20, "2010": 20},
                                    "range": {"2009": 2, "2010": 2},
                                    "units": "years",
                                    "source": "EIA AEO"}}},
                        "supply": {
                            "boiler (electric)": {
                                "performance": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 2, "2010": 2},
                                    "best": {"2009": 2, "2010": 2},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 20, "2010": 20},
                                    "range": {"2009": 2, "2010": 2},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "ASHP": {
                                "performance": {
                                    "typical": {"2009": 3, "2010": 3},
                                    "best": {"2009": 3, "2010": 3},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 3, "2010": 3},
                                    "best": {"2009": 3, "2010": 3},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 30, "2010": 30},
                                    "range": {"2009": 3, "2010": 3},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "GSHP": {
                                "performance": {
                                    "typical": {"2009": 4, "2010": 4},
                                    "best": {"2009": 4, "2010": 4},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 4, "2010": 4},
                                    "best": {"2009": 4, "2010": 4},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 40, "2010": 40},
                                    "range": {"2009": 4, "2010": 4},
                                    "units": "years",
                                    "source": "EIA AEO"}}}},
                    "secondary heating": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 5, "2010": 5},
                                    "best": {"2009": 5, "2010": 5},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 5, "2010": 5},
                                    "best": {"2009": 5, "2010": 5},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 50, "2010": 50},
                                    "range": {"2009": 5, "2010": 5},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 6, "2010": 6},
                                    "best": {"2009": 6, "2010": 6},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 6, "2010": 6},
                                    "best": {"2009": 6, "2010": 6},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 60, "2010": 60},
                                    "range": {"2009": 6, "2010": 6},
                                    "units": "years",
                                    "source": "EIA AEO"}}},
                        "supply": {
                            "non-specific": {
                                "performance": {
                                    "typical": {"2009": 7, "2010": 7},
                                    "best": {"2009": 7, "2010": 7},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 7, "2010": 7},
                                    "best": {"2009": 7, "2010": 7},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 70, "2010": 70},
                                    "range": {"2009": 7, "2010": 7},
                                    "units": "years",
                                    "source": "EIA AEO"}}}},
                    "cooling": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 8, "2010": 8},
                                    "best": {"2009": 8, "2010": 8},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 8, "2010": 8},
                                    "best": {"2009": 8, "2010": 8},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 80, "2010": 80},
                                    "range": {"2009": 8, "2010": 8},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 9, "2010": 9},
                                    "best": {"2009": 9, "2010": 9},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 9, "2010": 9},
                                    "best": {"2009": 9, "2010": 9},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 90, "2010": 90},
                                    "range": {"2009": 9, "2010": 9},
                                    "units": "years",
                                    "source": "EIA AEO"}}},
                        "supply": {
                            "central AC": {
                                "performance": {
                                    "typical": {"2009": 10, "2010": 10},
                                    "best": {"2009": 10, "2010": 10},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 10, "2010": 10},
                                    "best": {"2009": 10, "2010": 10},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 100, "2010": 100},
                                    "range": {"2009": 10, "2010": 10},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "room AC": {
                                "performance": {
                                    "typical": {"2009": 11, "2010": 11},
                                    "best": {"2009": 11, "2010": 11},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 11, "2010": 11},
                                    "best": {"2009": 11, "2010": 11},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 110, "2010": 110},
                                    "range": {"2009": 11, "2010": 11},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "ASHP": {
                                "performance": {
                                    "typical": {"2009": 12, "2010": 12},
                                    "best": {"2009": 12, "2010": 12},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 12, "2010": 12},
                                    "best": {"2009": 12, "2010": 12},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 120, "2010": 120},
                                    "range": {"2009": 12, "2010": 12},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "GSHP": {
                                "performance": {
                                    "typical": {"2009": 13, "2010": 13},
                                    "best": {"2009": 13, "2010": 13},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 13, "2010": 13},
                                    "best": {"2009": 13, "2010": 13},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 130, "2010": 130},
                                    "range": {"2009": 13, "2010": 13},
                                    "units": "years",
                                    "source": "EIA AEO"}}}},
                    "lighting": {
                        "linear fluorescent (LED)": {
                                "performance": {
                                    "typical": {"2009": 14, "2010": 14},
                                    "best": {"2009": 14, "2010": 14},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 14, "2010": 14},
                                    "best": {"2009": 14, "2010": 14},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 140, "2010": 140},
                                    "range": {"2009": 14, "2010": 14},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "general service (LED)": {
                                "performance": {
                                    "typical": {"2009": 15, "2010": 15},
                                    "best": {"2009": 15, "2010": 15},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 15, "2010": 15},
                                    "best": {"2009": 15, "2010": 15},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 150, "2010": 150},
                                    "range": {"2009": 15, "2010": 15},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "reflector (LED)": {
                                "performance": {
                                    "typical": {"2009": 16, "2010": 16},
                                    "best": {"2009": 16, "2010": 16},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 16, "2010": 16},
                                    "best": {"2009": 16, "2010": 16},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 160, "2010": 160},
                                    "range": {"2009": 16, "2010": 16},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "external (LED)": {
                                "performance": {
                                    "typical": {"2009": 17, "2010": 17},
                                    "best": {"2009": 17, "2010": 17},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 17, "2010": 17},
                                    "best": {"2009": 17, "2010": 17},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 170, "2010": 170},
                                    "range": {"2009": 17, "2010": 17},
                                    "units": "years",
                                    "source": "EIA AEO"}}}},
                "natural gas": {
                    "water heating": {
                            "performance": {
                                "typical": {"2009": 18, "2010": 18},
                                "best": {"2009": 18, "2010": 18},
                                "units": "EF",
                                "source":
                                "EIA AEO"},
                            "installed cost": {
                                "typical": {"2009": 18, "2010": 18},
                                "best": {"2009": 18, "2010": 18},
                                "units": "2014$/unit",
                                "source": "EIA AEO"},
                            "lifetime": {
                                "average": {"2009": 180, "2010": 180},
                                "range": {"2009": 18, "2010": 18},
                                "units": "years",
                                "source": "EIA AEO"}}}},
            "multi family home": {
                "electricity (grid)": {
                    "heating": {
                        "demand": {
                            "windows conduction": {
                                "performance": {
                                    "typical": {"2009": 19, "2010": 19},
                                    "best": {"2009": 19, "2010": 19},
                                    "units": "R Value",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 19, "2010": 19},
                                    "best": {"2009": 19, "2010": 19},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 190, "2010": 190},
                                    "range": {"2009": 19, "2010": 19},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "windows solar": {
                                "performance": {
                                    "typical": {"2009": 20, "2010": 20},
                                    "best": {"2009": 20, "2010": 20},
                                    "units": "SHGC",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 20, "2010": 20},
                                    "best": {"2009": 20, "2010": 20},
                                    "units": "2014$/sf",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 200, "2010": 200},
                                    "range": {"2009": 20, "2010": 20},
                                    "units": "years",
                                    "source": "EIA AEO"}}},
                        "supply": {
                            "boiler (electric)": {
                                "performance": {
                                    "typical": {"2009": 21, "2010": 21},
                                    "best": {"2009": 21, "2010": 21},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 21, "2010": 21},
                                    "best": {"2009": 21, "2010": 21},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 210, "2010": 210},
                                    "range": {"2009": 21, "2010": 21},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "ASHP": {
                                "performance": {
                                    "typical": {"2009": 22, "2010": 22},
                                    "best": {"2009": 22, "2010": 22},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 22, "2010": 22},
                                    "best": {"2009": 22, "2010": 22},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 220, "2010": 220},
                                    "range": {"2009": 22, "2010": 22},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                            "GSHP": {
                                "performance": {
                                    "typical": {"2009": 23, "2010": 23},
                                    "best": {"2009": 23, "2010": 23},
                                    "units": "COP",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 23, "2010": 23},
                                    "best": {"2009": 23, "2010": 23},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 230, "2010": 230},
                                    "range": {"2009": 23, "2010": 23},
                                    "units": "years",
                                    "source": "EIA AEO"}}}},
                    "lighting": {
                        "linear fluorescent (LED)": {
                                "performance": {
                                    "typical": {"2009": 24, "2010": 24},
                                    "best": {"2009": 24, "2010": 24},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 24, "2010": 24},
                                    "best": {"2009": 24, "2010": 24},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 240, "2010": 240},
                                    "range": {"2009": 24, "2010": 24},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "general service (LED)": {
                                "performance": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 250, "2010": 250},
                                    "range": {"2009": 25, "2010": 25},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "reflector (LED)": {
                                "performance": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 250, "2010": 250},
                                    "range": {"2009": 25, "2010": 25},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "external (LED)": {
                                "performance": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 250, "2010": 250},
                                    "range": {"2009": 25, "2010": 25},
                                    "units": "years",
                                    "source": "EIA AEO"}}}}}},
        "AIA_CZ4": {
            "multi family home": {
                "electricity (grid)": {
                    "lighting": {
                        "linear fluorescent (LED)": {
                                "performance": {
                                    "typical": {"2009": 24, "2010": 24},
                                    "best": {"2009": 24, "2010": 24},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 24, "2010": 24},
                                    "best": {"2009": 24, "2010": 24},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 240, "2010": 240},
                                    "range": {"2009": 24, "2010": 24},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "general service (LED)": {
                                "performance": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 25, "2010": 25},
                                    "best": {"2009": 25, "2010": 25},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 250, "2010": 250},
                                    "range": {"2009": 25, "2010": 25},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "reflector (LED)": {
                                "performance": {
                                    "typical": {"2009": 26, "2010": 26},
                                    "best": {"2009": 26, "2010": 26},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 26, "2010": 26},
                                    "best": {"2009": 26, "2010": 26},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 260, "2010": 260},
                                    "range": {"2009": 26, "2010": 26},
                                    "units": "years",
                                    "source": "EIA AEO"}},
                        "external (LED)": {
                                "performance": {
                                    "typical": {"2009": 27, "2010": 27},
                                    "best": {"2009": 27, "2010": 27},
                                    "units": "lm/W",
                                    "source":
                                    "EIA AEO"},
                                "installed cost": {
                                    "typical": {"2009": 27, "2010": 27},
                                    "best": {"2009": 27, "2010": 27},
                                    "units": "2014$/unit",
                                    "source": "EIA AEO"},
                                "lifetime": {
                                    "average": {"2009": 270, "2010": 270},
                                    "range": {"2009": 27, "2010": 27},
                                    "units": "years",
                                    "source": "EIA AEO"}}}}}}}

    # Sample input dict of microsegment stock/energy info. to reference in
    # generating and partitioning master microsegments for a measure
    sample_msegin = {
        "AIA_CZ1": {
            "assembly": {
                "electricity (grid)": {
                    "heating": {"demand": {"windows conduction": {
                                           "stock": "NA",
                                           "energy": {"2009": 0, "2010": 0}},
                                           "windows solar": {
                                           "stock": "NA",
                                           "energy": {"2009": 1, "2010": 1}},
                                           "lights": {
                                           "stock": "NA",
                                           "energy": {"2009": 1, "2010": 1}}}},
                    "secondary heating": {"demand": {"windows conduction": {
                                                     "stock": "NA",
                                                     "energy": {"2009": 5,
                                                                "2010": 5}},
                                                     "windows solar": {
                                                     "stock": "NA",
                                                     "energy": {"2009": 6,
                                                                "2010": 6}},
                                                     "lights": {
                                                     "stock": "NA",
                                                     "energy": {"2009": 6,
                                                                "2010": 6}}}},
                    "cooling": {"demand": {"windows conduction": {
                                           "stock": "NA",
                                           "energy": {"2009": 5, "2010": 5}},
                                           "windows solar": {
                                           "stock": "NA",
                                           "energy": {"2009": 6, "2010": 6}},
                                           "lights": {
                                           "stock": "NA",
                                           "energy": {"2009": 6, "2010": 6}}}},
                    "lighting": {"commercial light type X": {
                                 "stock": {"2009": 11, "2010": 11},
                                 "energy": {"2009": 11, "2010": 11}}}}},
            "single family home": {
                "square footage": {"2009": 100, "2010": 200},
                "total homes": {"2009": 1000, "2010": 1000},
                "new homes": {"2009": 100, "2010": 50},
                "electricity (grid)": {
                    "heating": {"demand": {"windows conduction": {
                                           "stock": "NA",
                                           "energy": {"2009": 0, "2010": 0}},
                                           "windows solar": {
                                           "stock": "NA",
                                           "energy": {"2009": 1, "2010": 1}}},
                                "supply": {"boiler (electric)": {
                                           "stock": {"2009": 2, "2010": 2},
                                           "energy": {"2009": 2, "2010": 2}},
                                           "ASHP": {
                                           "stock": {"2009": 3, "2010": 3},
                                           "energy": {"2009": 3, "2010": 3}},
                                           "GSHP": {
                                           "stock": {"2009": 4, "2010": 4},
                                           "energy": {"2009": 4, "2010": 4}}}},
                    "secondary heating": {"demand": {"windows conduction": {
                                                     "stock": "NA",
                                                     "energy": {"2009": 5,
                                                                "2010": 5}},
                                                     "windows solar": {
                                                     "stock": "NA",
                                                     "energy": {"2009": 6,
                                                                "2010": 6}}},
                                          "supply": {"non-specific": 7}},
                    "cooling": {"demand": {"windows conduction": {
                                           "stock": "NA",
                                           "energy": {"2009": 5, "2010": 5}},
                                           "windows solar": {
                                           "stock": "NA",
                                           "energy": {"2009": 6, "2010": 6}}},
                                "supply": {"central AC": {
                                           "stock": {"2009": 7, "2010": 7},
                                           "energy": {"2009": 7, "2010": 7}},
                                           "room AC": {
                                           "stock": {"2009": 8, "2010": 8},
                                           "energy": {"2009": 8, "2010": 8}},
                                           "ASHP": {
                                           "stock": {"2009": 9, "2010": 9},
                                           "energy": {"2009": 9, "2010": 9}},
                                           "GSHP": {
                                           "stock": {"2009": 10, "2010": 10},
                                           "energy": {"2009": 10,
                                                      "2010": 10}}}},
                    "lighting": {"linear fluorescent (LED)": {
                                 "stock": {"2009": 11, "2010": 11},
                                 "energy": {"2009": 11, "2010": 11}},
                                 "general service (LED)": {
                                 "stock": {"2009": 12, "2010": 12},
                                 "energy": {"2009": 12, "2010": 12}},
                                 "reflector (LED)": {
                                 "stock": {"2009": 13, "2010": 13},
                                 "energy": {"2009": 13, "2010": 13}},
                                 "external (LED)": {
                                 "stock": {"2009": 14, "2010": 14},
                                 "energy": {"2009": 14, "2010": 14}}}},
                "natural gas": {
                    "water heating": {
                        "stock": {"2009": 15, "2010": 15},
                        "energy": {"2009": 15, "2010": 15}},
                    "heating": {
                        "demand": {
                            "windows conduction": {
                                "stock": "NA",
                                "energy": {"2009": 0,
                                           "2010": 0}},
                            "windows solar": {
                                "stock": "NA",
                                "energy": {"2009": 1,
                                           "2010": 1}}}},
                    "secondary heating": {
                        "demand": {
                            "windows conduction": {
                                "stock": "NA",
                                "energy": {"2009": 5,
                                           "2010": 5}},
                            "windows solar": {
                                "stock": "NA",
                                "energy": {"2009": 6,
                                           "2010": 6}}}},
                    "cooling": {
                        "demand": {
                            "windows conduction": {
                                "stock": "NA",
                                "energy": {"2009": 5, "2010": 5}},
                            "windows solar": {
                                "stock": "NA",
                                "energy": {"2009": 6, "2010": 6}}}}}},
            "multi family home": {
                "square footage": {"2009": 300, "2010": 400},
                "total homes": {"2009": 1000, "2010": 1000},
                "new homes": {"2009": 100, "2010": 50},
                "electricity (grid)": {
                    "heating": {"demand": {"windows conduction": {
                                           "stock": "NA",
                                           "energy": {"2009": 0, "2010": 0}},
                                           "windows solar": {
                                           "stock": "NA",
                                           "energy": {"2009": 1, "2010": 1}}},
                                "supply": {"boiler (electric)": {
                                           "stock": {"2009": 2, "2010": 2},
                                           "energy": {"2009": 2, "2010": 2}},
                                           "ASHP": {
                                           "stock": {"2009": 3, "2010": 3},
                                           "energy": {"2009": 3, "2010": 3}},
                                           "GSHP": {
                                           "stock": {"2009": 4, "2010": 4}}}},
                    "lighting": {"linear fluorescent (LED)": {
                                 "stock": {"2009": 11, "2010": 11},
                                 "energy": {"2009": 11, "2010": 11}},
                                 "general service (LED)": {
                                 "stock": {"2009": 12, "2010": 12},
                                 "energy": {"2009": 12, "2010": 12}},
                                 "reflector (LED)": {
                                 "stock": {"2009": 13, "2010": 13},
                                 "energy": {"2009": 13, "2010": 13}},
                                 "external (LED)": {
                                 "stock": {"2009": 14, "2010": 14},
                                 "energy": {"2009": 14, "2010": 14}}}}}},
        "AIA_CZ2": {
            "single family home": {
                "square footage": {"2009": 500, "2010": 600},
                "total homes": {"2009": 1000, "2010": 1000},
                "new homes": {"2009": 100, "2010": 50},
                "electricity (grid)": {
                    "heating": {"demand": {"windows conduction": {
                                           "stock": "NA",
                                           "energy": {"2009": 0, "2010": 0}},
                                           "windows solar": {
                                           "stock": "NA",
                                           "energy": {"2009": 1, "2010": 1}}},
                                "supply": {"boiler (electric)": {
                                           "stock": {"2009": 2, "2010": 2},
                                           "energy": {"2009": 2, "2010": 2}},
                                           "ASHP": {
                                           "stock": {"2009": 3, "2010": 3},
                                           "energy": {"2009": 3, "2010": 3}},
                                           "GSHP": {
                                           "stock": {"2009": 4, "2010": 4},
                                           "energy": {"2009": 4, "2010": 4}}}},
                    "secondary heating": {"demand": {"windows conduction": {
                                                     "stock": "NA",
                                                     "energy": {"2009": 5,
                                                                "2010": 5}},
                                                     "windows solar": {
                                                     "stock": "NA",
                                                     "energy": {"2009": 6,
                                                                "2010": 6}}},
                                          "supply": {"non-specific": 7}},
                    "cooling": {"demand": {"windows conduction": {
                                           "stock": "NA",
                                           "energy": {"2009": 5, "2010": 5}},
                                           "windows solar": {
                                           "stock": "NA",
                                           "energy": {"2009": 6, "2010": 6}}},
                                "supply": {"central AC": {
                                           "stock": {"2009": 7, "2010": 7},
                                           "energy": {"2009": 7, "2010": 7}},
                                           "room AC": {
                                           "stock": {"2009": 8, "2010": 8},
                                           "energy": {"2009": 8, "2010": 8}},
                                           "ASHP": {
                                           "stock": {"2009": 9, "2010": 9},
                                           "energy": {"2009": 9, "2010": 9}},
                                           "GSHP": {
                                           "stock": {"2009": 10, "2010": 10},
                                           "energy": {"2009": 10,
                                                      "2010": 10}}}},
                    "lighting": {"linear fluorescent (LED)": {
                                 "stock": {"2009": 11, "2010": 11},
                                 "energy": {"2009": 11, "2010": 11}},
                                 "general service (LED)": {
                                 "stock": {"2009": 12, "2010": 12},
                                 "energy": {"2009": 12, "2010": 12}},
                                 "reflector (LED)": {
                                 "stock": {"2009": 13, "2010": 13},
                                 "energy": {"2009": 13, "2010": 13}},
                                 "external (LED)": {
                                 "stock": {"2009": 14, "2010": 14},
                                 "energy": {"2009": 14, "2010": 14}}}},
                "natural gas": {"water heating": {
                                "stock": {"2009": 15, "2010": 15},
                                "energy": {"2009": 15, "2010": 15}}}},
            "multi family home": {
                "square footage": {"2009": 700, "2010": 800},
                "total homes": {"2009": 1000, "2010": 1000},
                "new homes": {"2009": 100, "2010": 50},
                "electricity (grid)": {
                    "heating": {"demand": {"windows conduction": {
                                           "stock": "NA",
                                           "energy": {"2009": 0, "2010": 0}},
                                           "windows solar": {
                                           "stock": "NA",
                                           "energy": {"2009": 1, "2010": 1}}},
                                "supply": {"boiler (electric)": {
                                           "stock": {"2009": 2, "2010": 2},
                                           "energy": {"2009": 2, "2010": 2}},
                                           "ASHP": {
                                           "stock": {"2009": 3, "2010": 3},
                                           "energy": {"2009": 3, "2010": 3}},
                                           "GSHP": {
                                           "stock": {"2009": 4, "2010": 4}}}},
                    "lighting": {"linear fluorescent (LED)": {
                                 "stock": {"2009": 11, "2010": 11},
                                 "energy": {"2009": 11, "2010": 11}},
                                 "general service (LED)": {
                                 "stock": {"2009": 12, "2010": 12},
                                 "energy": {"2009": 12, "2010": 12}},
                                 "reflector (LED)": {
                                 "stock": {"2009": 13, "2010": 13},
                                 "energy": {"2009": 13, "2010": 13}},
                                 "external (LED)": {
                                 "stock": {"2009": 14, "2010": 14},
                                 "energy": {"2009": 14, "2010": 14}}}}}},
        "AIA_CZ4": {
            "multi family home": {
                "square footage": {"2009": 900, "2010": 1000},
                "total homes": {"2009": 1000, "2010": 1000},
                "new homes": {"2009": 100, "2010": 50},
                "electricity (grid)": {
                    "lighting": {"linear fluorescent (LED)": {
                                 "stock": {"2009": 11, "2010": 11},
                                 "energy": {"2009": 11, "2010": 11}},
                                 "general service (LED)": {
                                 "stock": {"2009": 12, "2010": 12},
                                 "energy": {"2009": 12, "2010": 12}},
                                 "reflector (LED)": {
                                 "stock": {"2009": 13, "2010": 13},
                                 "energy": {"2009": 13, "2010": 13}},
                                 "external (LED)": {
                                 "stock": {"2009": 14, "2010": 14},
                                 "energy": {"2009": 14, "2010": 14}}}}}}}

    # List of measures with attribute combinations that should all be found in
    # the key chains of the "sample_msegin" dict above
    ok_measures = [{"name": "sample measure 1",
                    "installed_cost": 25,
                    "cost_units": "2014$/unit",
                    "energy_efficiency": {"primary":
                                          {"AIA_CZ1": {"heating": 30,
                                                       "cooling": 25},
                                           "AIA_CZ2": {"heating": 30,
                                                       "cooling": 15}},
                                          "secondary": None},
                    "energy_efficiency_units": {"primary": "COP",
                                                "secondary": None},
                    "market_entry_year": None,
                    "market_exit_year": None,
                    "product_lifetime": 10,
                    "structure_type": ["new", "existing"],
                    "bldg_type": "single family home",
                    "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                    "fuel_type": {"primary": "electricity (grid)",
                                  "secondary": None},
                    "end_use": {"primary": ["heating", "cooling"],
                                "secondary": None},
                    "technology_type": {"primary": "supply",
                                        "secondary": "demand"},
                    "technology": {"primary": ["boiler (electric)",
                                   "ASHP", "GSHP", "room AC"],
                                   "secondary": None}},
                   {"name": "sample measure 2",
                    "installed_cost": 25,
                    "cost_units": "2014$/unit",
                    "energy_efficiency": {"primary": 25,
                                          "secondary": None},
                    "energy_efficiency_units": {"primary": "EF",
                                                "secondary": None},
                    "market_entry_year": None,
                    "market_exit_year": None,
                    "product_lifetime": 10,
                    "structure_type": ["new", "existing"],
                    "bldg_type": "single family home",
                    "climate_zone": "AIA_CZ1",
                    "fuel_type": {"primary": "natural gas",
                                  "secondary": None},
                    "end_use": {"primary": "water heating",
                                "secondary": None},
                    "technology_type": {"primary": "supply",
                                        "secondary": None},
                    "technology": {"primary": None,
                                   "secondary": None}},
                   {"name": "sample measure 3",
                    "installed_cost": 25,
                    "cost_units": "2014$/unit",
                    "energy_efficiency": {"primary": 25,
                                          "secondary": {
                                              "heating": 0.4,
                                              "secondary heating": 0.4,
                                              "cooling": -0.4}},
                    "energy_efficiency_units": {"primary": "lm/W",
                                                "secondary":
                                                "relative savings"},
                    "market_entry_year": None,
                    "market_exit_year": None,
                    "product_lifetime": 10,
                    "structure_type": ["new", "existing"],
                    "bldg_type": ["single family home",
                                  "multi family home"],
                    "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                    "fuel_type": {"primary": "electricity (grid)",
                                  "secondary": ["electricity (grid)",
                                                "natural gas"]},
                    "end_use": {"primary": "lighting",
                                "secondary": ["heating", "secondary heating",
                                              "cooling"]},
                    "technology_type": {"primary": "supply",
                                        "secondary": "demand"},
                    "technology": {"primary":
                                   ["linear fluorescent (LED)",
                                    "general service (LED)",
                                    "external (LED)"],
                                   "secondary":
                                   ["windows conduction",
                                    "windows solar"]}},
                   {"name": "sample measure 4",
                    "installed_cost": 10,
                    "cost_units": "2014$/sf",
                    "energy_efficiency": {"primary":
                                          {"windows conduction": 20,
                                           "windows solar": 1},
                                          "secondary": None},
                    "energy_efficiency_units": {"primary":
                                                {"windows conduction":
                                                 "R Value",
                                                 "windows solar": "SHGC"},
                                                "secondary": None},
                    "market_entry_year": None,
                    "market_exit_year": None,
                    "product_lifetime": 10,
                    "structure_type": ["new", "existing"],
                    "bldg_type": ["single family home",
                                  "multi family home"],
                    "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                    "fuel_type": {"primary": "electricity (grid)",
                                  "secondary": None},
                    "end_use": {"primary": "heating",
                                "secondary": None},
                    "technology_type": {"primary": "demand",
                                        "secondary": None},
                    "technology": {"primary": ["windows conduction",
                                   "windows solar"],
                                   "secondary": None}},
                   {"name": "sample measure 5",
                    "installed_cost": 10,
                    "cost_units": "2014$/sf",
                    "energy_efficiency": {"primary": 1, "secondary": None},
                    "energy_efficiency_units": {"primary": "SHGC",
                                                "secondary": None},
                    "market_entry_year": None,
                    "market_exit_year": None,
                    "product_lifetime": 10,
                    "structure_type": ["new", "existing"],
                    "bldg_type": "single family home",
                    "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                    "fuel_type": {"primary": "electricity (grid)",
                                  "secondary": None},
                    "end_use": {"primary": "heating",
                                "secondary": None},
                    "technology_type": {"primary": "demand",
                                        "secondary": None},
                    "technology": {"primary": "windows solar",
                                   "secondary": None}},
                   {"name": "sample measure 6",
                    "installed_cost": 10,
                    "cost_units": "2014$/sf",
                    "energy_efficiency": {"primary": {"windows conduction": 10,
                                                      "windows solar": 1},
                                          "secondary": None},
                    "energy_efficiency_units": {"primary":
                                                {"windows conduction":
                                                 "R Value",
                                                 "windows solar": "SHGC"},
                                                "secondary": None},
                    "market_entry_year": None,
                    "market_exit_year": None,
                    "product_lifetime": 10,
                    "structure_type": ["new", "existing"],
                    "bldg_type": "single family home",
                    "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                    "fuel_type": {"primary": "electricity (grid)",
                                  "secondary": None},
                    "end_use": {"primary": ["heating", "secondary heating",
                                            "cooling"],
                                "secondary": None},
                    "technology_type": {"primary": "demand",
                                        "secondary": None},
                    "technology": {"primary": ["windows conduction",
                                               "windows solar"],
                                   "secondary": None}},
                   {"name": "sample measure 7",
                    "installed_cost": 10,
                    "cost_units": "2014$/sf",
                    "energy_efficiency": {"primary":
                                          {"windows conduction": 0.4,
                                           "windows solar": 1},
                                          "secondary": None},
                    "energy_efficiency_units": {"primary":
                                                {"windows conduction":
                                                 "relative savings",
                                                 "windows solar": "SHGC"},
                                                "secondary": None},
                    "market_entry_year": None,
                    "market_exit_year": None,
                    "product_lifetime": 10,
                    "structure_type": ["new", "existing"],
                    "bldg_type": "single family home",
                    "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                    "fuel_type": {"primary": "electricity (grid)",
                                  "secondary": None},
                    "end_use": {"primary": ["heating", "secondary heating",
                                            "cooling"],
                                "secondary": None},
                    "technology_type": {"primary": "demand",
                                        "secondary": None},
                    "technology": {"primary": ["windows conduction",
                                               "windows solar"],
                                   "secondary": None}},
                   {"name": "sample measure 8",  # Add heat/cool end uses later
                    "installed_cost": 25,
                    "cost_units": "2014$/unit",
                    "energy_efficiency": {"primary": 25,
                                          "secondary": None},
                    "energy_efficiency_units": {"primary": "lm/W",
                                                "secondary": None},
                    "product_lifetime": 10,
                    "structure_type": ["new", "existing"],
                    "bldg_type": "assembly",
                    "climate_zone": "AIA_CZ1",
                    "fuel_type": {"primary": "electricity (grid)",
                                  "secondary": ["electricity (grid)",
                                                "natural gas"]},
                    "end_use": {"primary": "lighting",
                                "secondary": None},
                    "market_entry_year": None,
                    "market_exit_year": None,
                    "technology_type": {"primary": "supply",
                                        "secondary": None},
                    "technology": {"primary":
                                   "commercial light type X",
                                   "secondary": None}},
                   {"name": "sample measure 9",
                    "installed_cost": 25,
                    "cost_units": "2014$/unit",
                    "energy_efficiency": {"primary": 25,
                                          "secondary": None},
                    "energy_efficiency_units": {"primary": "EF",
                                                "secondary": None},
                    "product_lifetime": 10,
                    "structure_type": "new",
                    "bldg_type": "single family home",
                    "climate_zone": "AIA_CZ1",
                    "fuel_type": {"primary": "natural gas",
                                  "secondary": None},
                    "end_use": {"primary": "water heating",
                                "secondary": None},
                    "market_entry_year": None,
                    "market_exit_year": None,
                    "technology_type": {"primary": "supply",
                                        "secondary": None},
                    "technology": {"primary": None,
                                   "secondary": None}},
                   {"name": "sample measure 10",
                    "installed_cost": 25,
                    "cost_units": "2014$/unit",
                    "energy_efficiency": {"primary": 25,
                                          "secondary": None},
                    "energy_efficiency_units": {"primary": "EF",
                                                "secondary": None},
                    "market_entry_year": None,
                    "market_exit_year": None,
                    "product_lifetime": 10,
                    "structure_type": "existing",
                    "bldg_type": "single family home",
                    "climate_zone": "AIA_CZ1",
                    "fuel_type": {"primary": "natural gas",
                                  "secondary": None},
                    "end_use": {"primary": "water heating",
                                "secondary": None},
                    "technology_type": {"primary": "supply",
                                        "secondary": None},
                    "technology": {"primary": None,
                                   "secondary": None}},
                   {"name": "sample measure 11",
                    "installed_cost": 25,
                    "cost_units": "2014$/unit",
                    "energy_efficiency": {"primary": 25,
                                          "secondary": {
                                              "heating": 0.4,
                                              "secondary heating": 0.4,
                                              "cooling": -0.4}},
                    "energy_efficiency_units": {"primary": "lm/W",
                                                "secondary":
                                                "relative savings"},
                    "market_entry_year": 2010,
                    "market_exit_year": None,
                    "product_lifetime": 10,
                    "structure_type": ["new", "existing"],
                    "bldg_type": ["single family home",
                                  "multi family home"],
                    "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                    "fuel_type": {"primary": "electricity (grid)",
                                  "secondary": ["electricity (grid)",
                                                "natural gas"]},
                    "end_use": {"primary": "lighting",
                                "secondary": ["heating", "secondary heating",
                                              "cooling"]},
                    "technology_type": {"primary": "supply",
                                        "secondary": "demand"},
                    "technology": {"primary":
                                   ["linear fluorescent (LED)",
                                    "general service (LED)",
                                    "external (LED)"],
                                   "secondary":
                                   ["windows conduction",
                                    "windows solar"]}},
                   {"name": "sample measure 12",
                    "installed_cost": 25,
                    "cost_units": "2014$/unit",
                    "energy_efficiency": {"primary": 25,
                                          "secondary": {
                                              "heating": 0.4,
                                              "secondary heating": 0.4,
                                              "cooling": -0.4}},
                    "energy_efficiency_units": {"primary": "lm/W",
                                                "secondary":
                                                "relative savings"},
                    "market_entry_year": None,
                    "market_exit_year": 2010,
                    "product_lifetime": 10,
                    "structure_type": ["new", "existing"],
                    "bldg_type": ["single family home",
                                  "multi family home"],
                    "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                    "fuel_type": {"primary": "electricity (grid)",
                                  "secondary": ["electricity (grid)",
                                                "natural gas"]},
                    "end_use": {"primary": "lighting",
                                "secondary": ["heating", "secondary heating",
                                              "cooling"]},
                    "technology_type": {"primary": "supply",
                                        "secondary": "demand"},
                    "technology": {"primary":
                                   ["linear fluorescent (LED)",
                                    "general service (LED)",
                                    "external (LED)"],
                                   "secondary":
                                   ["windows conduction",
                                    "windows solar"]}}]

    # List of selected "ok" measures above with certain inputs now specified
    # as probability distributions
    ok_measures_dist = [{"name": "distrib measure 1",
                         "installed_cost": ["normal", 25, 5],
                         "cost_units": "2014$/unit",
                         "energy_efficiency": {"primary":
                                               {"AIA_CZ1": {"heating":
                                                            ["normal", 30, 1],
                                                            "cooling":
                                                            ["normal", 25, 2]},
                                                "AIA_CZ2": {"heating": 30,
                                                            "cooling":
                                                            ["normal", 15,
                                                             4]}},
                                               "secondary": None},
                         "energy_efficiency_units": {"primary": "COP",
                                                     "secondary": None},
                         "market_entry_year": None,
                         "market_exit_year": None,
                         "product_lifetime": 10,
                         "structure_type": ["new", "existing"],
                         "bldg_type": "single family home",
                         "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                         "fuel_type": {"primary": "electricity (grid)",
                                       "secondary": None},
                         "end_use": {"primary": ["heating", "cooling"],
                                     "secondary": None},
                         "technology_type": {"primary": "supply",
                                             "secondary": None},
                         "technology": {"primary": ["boiler (electric)",
                                        "ASHP", "GSHP", "room AC"],
                                        "secondary": None}},
                        {"name": "distrib measure 2",
                         "installed_cost": ["lognormal", 3.22, 0.06],
                         "cost_units": "2014$/unit",
                         "energy_efficiency": {"primary": ["normal", 25, 5],
                                               "secondary": None},
                         "energy_efficiency_units": {"primary": "EF",
                                                     "secondary": None},
                         "market_entry_year": None,
                         "market_exit_year": None,
                         "product_lifetime": ["normal", 10, 1],
                         "structure_type": ["new", "existing"],
                         "bldg_type": "single family home",
                         "climate_zone": "AIA_CZ1",
                         "fuel_type": {"primary": "natural gas",
                                       "secondary": None},
                         "end_use": {"primary": "water heating",
                                     "secondary": None},
                         "technology_type": {"primary": "supply",
                                             "secondary": None},
                         "technology": {"primary": None,
                                        "secondary": None}},
                        {"name": "distrib measure 3",
                         "installed_cost": ["normal", 10, 5],
                         "cost_units": "2014$/sf",
                         "energy_efficiency": {"primary":
                                               {"windows conduction":
                                                ["lognormal", 2.29, 0.14],
                                                "windows solar":
                                                ["normal", 1, 0.1]},
                                               "secondary": None},
                         "energy_efficiency_units": {"windows conduction":
                                                     "R Value",
                                                     "windows solar": "SHGC"},
                         "market_entry_year": None,
                         "market_exit_year": None,
                         "product_lifetime": 10,
                         "structure_type": ["new", "existing"],
                         "bldg_type": "single family home",
                         "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                         "fuel_type": {"primary": "electricity (grid)",
                                       "secondary": None},
                         "end_use": {"primary": ["heating",
                                                 "secondary heating",
                                                 "cooling"],
                                     "secondary": None},
                         "technology_type": {"primary": "demand",
                                             "secondary": None},
                         "technology": {"primary": ["windows conduction",
                                                    "windows solar"],
                                        "secondary": None}}]

    # List of measures with attribute combinations that should match some of
    # the key chains in the "sample_msegin" dict above (i.e., AIA_CZ1 ->
    # single family home -> electricity (grid) -> cooling -> GSHP is
    # a valid chain, AIA_CZ1 -> single family home -> electricity (grid) ->
    # cooling -> linear fluorescent is not)
    partial_measures = [{"name": "partial measure 1",
                         "installed_cost": 25,
                         "cost_units": "2014$/unit",
                         "energy_efficiency": {"primary": 25,
                                               "secondary": None},
                         "product_lifetime": 10,
                         "structure_type": ["new", "existing"],
                         "energy_efficiency_units": {"primary": "COP",
                                                     "secondary": None},
                         "market_entry_year": None,
                         "market_exit_year": None,
                         "bldg_type": "single family home",
                         "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                         "fuel_type": {"primary": "electricity (grid)",
                                       "secondary": None},
                         "end_use": {"primary": "cooling",
                                     "secondary": None},
                         "technology_type": {"primary": "supply",
                                             "secondary": None},
                         "technology": {"primary": ["boiler (electric)",
                                                    "ASHP"],
                                        "secondary": None}},
                        {"name": "partial measure 2",
                         "installed_cost": 25,
                         "cost_units": "2014$/unit",
                         "energy_efficiency": {"primary": 25,
                                               "secondary": None},
                         "market_entry_year": None,
                         "market_exit_year": None,
                         "product_lifetime": 10,
                         "structure_type": ["new", "existing"],
                         "energy_efficiency_units": {"primary": "COP",
                                                     "secondary": None},
                         "bldg_type": "single family home",
                         "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                         "fuel_type": {"primary": "electricity (grid)",
                                       "secondary": None},
                         "end_use": {"primary": ["heating", "cooling"],
                                     "secondary": None},
                         "technology_type": {"primary": "supply",
                                             "secondary": None},
                         "technology": {"primary":
                                        ["linear fluorescent (LED)",
                                         "general service (LED)",
                                         "external (LED)", "GSHP", "ASHP"],
                                        "secondary": None}}]

    # List of measures with attribute combinations that should not match any
    # of the key chains in the "sample_msegin" dict above
    blank_measures = [{"name": "blank measure 1",
                       "installed_cost": 10,
                       "cost_units": "2014$/unit",
                       "energy_efficiency": {"primary": 10,
                                             "secondary": None},
                       "energy_efficiency_units": {"primary": "COP",
                                                   "secondary": None},
                       "market_entry_year": None,
                       "market_exit_year": None,
                       "product_lifetime": 10,
                       "structure_type": ["new", "existing"],
                       "bldg_type": "single family home",
                       "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                       "fuel_type": {"primary": "electricity (grid)",
                                     "secondary": None},
                       "end_use": {"primary": "cooling",
                                   "secondary": None},
                       "technology_type": {"primary": "supply",
                                           "secondary": None},
                       "technology": {"primary": "boiler (electric)",
                                      "secondary": None}},
                      {"name": "blank measure 2",
                       "installed_cost": 10,
                       "cost_units": "2014$/unit",
                       "energy_efficiency": {"primary":
                                             {"AIA_CZ1": {"heating": 30,
                                                          "cooling": 25},
                                              "AIA_CZ2": {"heating": 30,
                                                          "cooling": 15}},
                                             "secondary": None},
                       "energy_efficiency_units": {"primary": "COP",
                                                   "secondary": None},
                       "market_entry_year": None,
                       "market_exit_year": None,
                       "product_lifetime": 10,
                       "structure_type": ["new", "existing"],
                       "bldg_type": "single family home",
                       "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                       "fuel_type": {"primary": "electricity (grid)",
                                     "secondary": None},
                       "end_use": {"primary": ["heating", "cooling"],
                                   "secondary": None},
                       "technology_type": {"primary": "supply",
                                           "secondary": None},
                       "technology": {"primary": ["linear fluorescent (LED)",
                                                  "general service (LED)",
                                                  "external (LED)"],
                                      "secondary": None}},
                      {"name": "blank measure 3",
                       "installed_cost": 25,
                       "cost_units": "2014$/unit",
                       "energy_efficiency": {"primary": 25, "secondary": None},
                       "product_lifetime": 10,
                       "structure_type": ["new", "existing"],
                       "energy_efficiency_units": {"primary": "lm/W",
                                                   "secondary": None},
                       "market_entry_year": None,
                       "market_exit_year": None,
                       "bldg_type": "single family home",
                       "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
                       "fuel_type": {"primary": "natural gas",
                                     "secondary": None},
                       "end_use": {"primary": "lighting",
                                   "secondary": ["heating",
                                                 "secondary heating",
                                                 "cooling"]},
                       "technology_type": {"primary": "supply",
                                           "secondary": "demand"},
                       "technology": {"primary":
                                      ["linear fluorescent (LED)",
                                       "general service (LED)",
                                       "external (LED)"],
                                      "secondary":
                                      ["windows conduction",
                                       "windows solar"]}},
                      {"name": "blank measure 4",
                       "installed_cost": 25,
                       "cost_units": "2014$/unit",
                       "energy_efficiency": {"primary": 25, "secondary": None},
                       "product_lifetime": 10,
                       "structure_type": ["new", "existing"],
                       "energy_efficiency_units": {"primary": "lm/W",
                                                   "secondary": None},
                       "market_entry_year": None,
                       "market_exit_year": None,
                       "bldg_type": "single family home",
                       "climate_zone": "AIA_CZ1",
                       "fuel_type": {"primary": "solar",
                                     "secondary": None},
                       "end_use": {"primary": "lighting",
                                   "secondary": ["heating",
                                                 "secondary heating",
                                                 "cooling"]},
                       "technology_type": {"primary": "supply",
                                           "secondary": "demand"},
                       "technology": {"primary":
                                      ["linear fluorescent (LED)",
                                       "general service (LED)",
                                       "external (LED)"],
                                      "secondary":
                                      ["windows conduction",
                                       "windows solar"]}}]

    # Master stock, energy, and cost information that should be generated by
    # "ok_measures" above using the "sample_msegin" dict
    ok_out = [{"stock": {"total": {"2009": 72, "2010": 72},
                         "competed": {"2009": 72, "2010": 72}},
               "energy": {"total": {"2009": 229.68, "2010": 230.4},
                          "competed": {"2009": 229.68, "2010": 230.4},
                          "efficient": {"2009": 117.0943, "2010": 117.4613}},
               "carbon": {"total": {"2009": 13056.63, "2010": 12941.16},
                          "competed": {"2009": 13056.63, "2010": 12941.16},
                          "efficient": {"2009": 6656.461, "2010": 6597.595}},
               "cost": {
                   "stock": {
                       "total": {"2009": 710, "2010": 710},
                       "competed": {"2009": 710, "2010": 710},
                       "efficient": {"2009": 1800, "2010": 1800}},
                   "energy": {
                       "total": {"2009": 2328.955, "2010": 2227.968},
                       "competed": {"2009": 2328.955, "2010": 2227.968},
                       "efficient": {"2009": 1187.336, "2010": 1135.851}},
                   "carbon": {
                       "total": {"2009": 430868.63, "2010": 427058.3},
                       "competed": {"2009": 430868.63, "2010": 427058.3},
                       "efficient": {"2009": 219663.21, "2010": 217720.65}}},
               "lifetime": {"baseline": {"2009": 75, "2010": 75},
                            "measure": 10}},
              {"stock": {"total": {"2009": 15, "2010": 15},
                         "competed": {"2009": 15, "2010": 15}},
               "energy": {"total": {"2009": 15.15, "2010": 15.15},
                          "competed": {"2009": 15.15, "2010": 15.15},
                          "efficient": {"2009": 10.908, "2010": 10.908}},
               "carbon": {"total": {"2009": 856.2139, "2010": 832.0021},
                          "competed": {"2009": 856.2139, "2010": 832.0021},
                          "efficient": {"2009": 616.474, "2010": 599.0415}},
               "cost": {
                   "stock": {
                       "total": {"2009": 270, "2010": 270},
                       "competed": {"2009": 270, "2010": 270},
                       "efficient": {"2009": 375, "2010": 375}},
                   "energy": {
                       "total": {"2009": 170.892, "2010": 163.317},
                       "competed": {"2009": 170.892, "2010": 163.317},
                       "efficient": {"2009": 123.0422, "2010": 117.5882}},
                   "carbon": {
                       "total": {"2009": 28255.06, "2010": 27456.07},
                       "competed": {"2009": 28255.06, "2010": 27456.07},
                       "efficient": {"2009": 20343.64, "2010": 19768.37}}},
               "lifetime": {"baseline": {"2009": 180, "2010": 180},
                            "measure": 10}},
              {"stock": {"total": {"2009": 148, "2010": 148},
                         "competed": {"2009": 148, "2010": 148}},
               "energy": {"total": {"2009": 648.47, "2010": 650.43},
                          "competed": {"2009": 648.47, "2010": 650.43},
                          "efficient": {"2009": 550.0692, "2010": 551.722}},
               "carbon": {"total": {"2009": 36855.9, "2010": 36504.45},
                          "competed": {"2009": 36855.9, "2010": 36504.45},
                          "efficient": {"2009": 31262.24, "2010": 30960.7}},
               "cost": {
                   "stock": {
                       "total": {"2009": 2972, "2010": 2972},
                       "competed": {"2009": 2972, "2010": 2972},
                       "efficient": {"2009": 3700, "2010": 3700}},
                   "energy": {
                       "total": {"2009": 6601.968, "2010": 6315.443},
                       "competed": {"2009": 6601.968, "2010": 6315.443},
                       "efficient": {"2009": 5603.723, "2010": 5360.489}},
                   "carbon": {
                       "total": {"2009": 1216244.58, "2010": 1204646.90},
                       "competed": {"2009": 1216244.58, "2010": 1204646.90},
                       "efficient": {"2009": 1031653.83, "2010": 1021703.20}}},
               "lifetime": {"baseline": {"2009": 200, "2010": 200},
                            "measure": 10}},
              {"stock": {"total": {"2009": 1600, "2010": 2000},
                         "competed": {"2009": 1600, "2010": 2000}},
               "energy": {"total": {"2009": 12.76, "2010": 12.8},
                          "competed": {"2009": 12.76, "2010": 12.8},
                          "efficient": {"2009": 3.509, "2010": 3.52}},
               "carbon": {"total": {"2009": 725.3681, "2010": 718.9534},
                          "competed": {"2009": 725.3681, "2010": 718.9534},
                          "efficient": {"2009": 199.4762, "2010": 197.7122}},
               "cost": {
                   "stock": {
                       "total": {"2009": 20400, "2010": 24600},
                       "competed": {"2009": 20400, "2010": 24600},
                       "efficient": {"2009": 16000, "2010": 20000}},
                   "energy": {
                       "total": {"2009": 129.3864, "2010": 123.776},
                       "competed": {"2009": 129.3864, "2010": 123.776},
                       "efficient": {"2009": 35.58126, "2010": 34.0384}},
                   "carbon": {
                       "total": {"2009": 23937.15, "2010": 23725.46},
                       "competed": {"2009": 23937.15, "2010": 23725.46},
                       "efficient": {"2009": 6582.715, "2010": 6524.502}}},
               "lifetime": {"baseline": {"2009": 105, "2010": 105},
                            "measure": 10}},
              {"stock": {"total": {"2009": 600, "2010": 800},
                         "competed": {"2009": 600, "2010": 800}},
               "energy": {"total": {"2009": 6.38, "2010": 6.4},
                          "competed": {"2009": 6.38, "2010": 6.4},
                          "efficient": {"2009": 3.19, "2010": 3.2}},
               "carbon": {"total": {"2009": 362.684, "2010": 359.4767},
                          "competed": {"2009": 362.684, "2010": 359.4767},
                          "efficient": {"2009": 181.342, "2010": 179.7383}},
               "cost": {
                   "stock": {
                       "total": {"2009": 1200, "2010": 1600},
                       "competed": {"2009": 1200, "2010": 1600},
                       "efficient": {"2009": 6000, "2010": 8000}},
                   "energy": {
                       "total": {"2009": 64.6932, "2010": 61.888},
                       "competed": {"2009": 64.6932, "2010": 61.888},
                       "efficient": {"2009": 32.3466, "2010": 30.944}},
                   "carbon": {
                       "total": {"2009": 11968.57, "2010": 11862.73},
                       "competed": {"2009": 11968.57, "2010": 11862.73},
                       "efficient": {"2009": 5984.287, "2010": 5931.365}}},
               "lifetime": {"baseline": {"2009": 20, "2010": 20},
                            "measure": 10}},
              {"stock": {"total": {"2009": 600, "2010": 800},
                         "competed": {"2009": 600, "2010": 800}},
               "energy": {"total": {"2009": 146.74, "2010": 147.2},
                          "competed": {"2009": 146.74, "2010": 147.2},
                          "efficient": {"2009": 55.29333, "2010": 55.46667}},
               "carbon": {"total": {"2009": 8341.733, "2010": 8267.964},
                          "competed": {"2009": 8341.733, "2010": 8267.964},
                          "efficient": {"2009": 3143.262, "2010": 3115.465}},
               "cost": {
                   "stock": {
                       "total": {"2009": 3100, "2010": 4133.33},
                       "competed": {"2009": 3100, "2010": 4133.33},
                       "efficient": {"2009": 6000, "2010": 8000}},
                   "energy": {
                       "total": {"2009": 1487.944, "2010": 1423.424},
                       "competed": {"2009": 1487.944, "2010": 1423.424},
                       "efficient": {"2009": 560.6744, "2010": 536.3627}},
                   "carbon": {
                       "total": {"2009": 275277.18, "2010": 272842.8},
                       "competed": {"2009": 275277.18, "2010": 272842.8},
                       "efficient": {"2009": 103727.63, "2010": 102810.33}}},
               "lifetime": {"baseline": {"2009": 51.67, "2010": 51.67},
                            "measure": 10}},
              {"stock": {"total": {"2009": 600, "2010": 800},
                         "competed": {"2009": 600, "2010": 800}},
               "energy": {"total": {"2009": 146.74, "2010": 147.2},
                          "competed": {"2009": 146.74, "2010": 147.2},
                          "efficient": {"2009": 52.10333, "2010": 52.26667}},
               "carbon": {"total": {"2009": 8341.733, "2010": 8267.964},
                          "competed": {"2009": 8341.733, "2010": 8267.964},
                          "efficient": {"2009": 2961.92, "2010": 2935.726}},
               "cost": {
                   "stock": {
                       "total": {"2009": 3100, "2010": 4133.33},
                       "competed": {"2009": 3100, "2010": 4133.33},
                       "efficient": {"2009": 6000, "2010": 8000}},
                   "energy": {
                       "total": {"2009": 1487.944, "2010": 1423.424},
                       "competed": {"2009": 1487.944, "2010": 1423.424},
                       "efficient": {"2009": 528.3278, "2010": 505.4187}},
                   "carbon": {
                       "total": {"2009": 275277.18, "2010": 272842.8},
                       "competed": {"2009": 275277.18, "2010": 272842.8},
                       "efficient": {"2009": 97743.35, "2010": 96878.97}}},
               "lifetime": {"baseline": {"2009": 51.67, "2010": 51.67},
                            "measure": 10}},
              {"stock": {"total": {"2009": 11, "2010": 11},
                         "competed": {"2009": 11, "2010": 11}},
               "energy": {"total": {"2009": 76.56, "2010": 76.8},
                          "competed": {"2009": 76.56, "2010": 76.8},
                          "efficient": {"2009": 62.524, "2010": 62.72}},
               "carbon": {"total": {"2009": 4352.208, "2010": 4313.72},
                          "competed": {"2009": 4352.208, "2010": 4313.72},
                          "efficient": {"2009": 3554.304, "2010": 3522.872}},
               "cost": {
                   "stock": {
                       "total": {"2009": 154, "2010": 154},
                       "competed": {"2009": 154, "2010": 154},
                       "efficient": {"2009": 275, "2010": 275}},
                   "energy": {
                       "total": {"2009": 695.1648, "2010": 656.64},
                       "competed": {"2009": 695.1648, "2010": 656.64},
                       "efficient": {"2009": 567.7179, "2010": 536.256}},
                   "carbon": {
                       "total": {"2009": 143622.88, "2010": 142352.77},
                       "competed": {"2009": 143622.88, "2010": 142352.77},
                       "efficient": {"2009": 117292.02, "2010": 116254.76}}},
               "lifetime": {"baseline": {"2009": 140, "2010": 140},
                            "measure": 10}},
              {"stock": {"total": {"2009": 1.5, "2010": 0.75},
                         "competed": {"2009": 1.5, "2010": 0.75}},
               "energy": {"total": {"2009": 1.515, "2010": 0.7575},
                          "competed": {"2009": 1.515, "2010": 0.7575},
                          "efficient": {"2009": 1.0908, "2010": 0.5454}},
               "carbon": {"total": {"2009": 85.62139, "2010": 41.60011},
                          "competed": {"2009": 85.62139, "2010": 41.60011},
                          "efficient": {"2009": 61.6474, "2010": 29.95208}},
               "cost": {
                   "stock": {
                       "total": {"2009": 27, "2010": 13.5},
                       "competed": {"2009": 27, "2010": 13.5},
                       "efficient": {"2009": 37.5, "2010": 18.75}},
                   "energy": {
                       "total": {"2009": 17.0892, "2010": 8.16585},
                       "competed": {"2009": 17.0892, "2010": 8.16585},
                       "efficient": {"2009": 12.30422, "2010": 5.87941}},
                   "carbon": {
                       "total": {"2009": 2825.506, "2010": 1372.803},
                       "competed": {"2009": 2825.506, "2010": 1372.803},
                       "efficient": {"2009": 2034.364, "2010": 988.4185}}},
               "lifetime": {"baseline": {"2009": 180, "2010": 180},
                            "measure": 10}},
              {"stock": {"total": {"2009": 13.5, "2010": 14.25},
                         "competed": {"2009": 13.5, "2010": 14.25}},
               "energy": {"total": {"2009": 13.635, "2010": 14.3925},
                          "competed": {"2009": 13.635, "2010": 14.3925},
                          "efficient": {"2009": 9.8172, "2010": 10.3626}},
               "carbon": {"total": {"2009": 770.5925, "2010": 790.402},
                          "competed": {"2009": 770.5925, "2010": 790.402},
                          "efficient": {"2009": 554.8266, "2010": 569.0894}},
               "cost": {
                   "stock": {
                       "total": {"2009": 243, "2010": 256.5},
                       "competed": {"2009": 243, "2010": 256.5},
                       "efficient": {"2009": 337.5, "2010": 356.25}},
                   "energy": {
                       "total": {"2009": 153.8028, "2010": 155.1512},
                       "competed": {"2009": 153.8028, "2010": 155.1512},
                       "efficient": {"2009": 110.738, "2010": 111.7088}},
                   "carbon": {
                       "total": {"2009": 25429.55, "2010": 26083.26},
                       "competed": {"2009": 25429.55, "2010": 26083.26},
                       "efficient": {"2009": 18309.28, "2010": 18779.95}}},
               "lifetime": {"baseline": {"2009": 180, "2010": 180},
                            "measure": 10}},
              {"stock": {"total": {"2009": 148, "2010": 148},
                         "competed": {"2009": 148, "2010": 148}},
               "energy": {"total": {"2009": 648.47, "2010": 650.43},
                          "competed": {"2009": 648.47, "2010": 650.43},
                          "efficient": {"2009": 648.47, "2010": 551.722}},
               "carbon": {"total": {"2009": 36855.9, "2010": 36504.45},
                          "competed": {"2009": 36855.9, "2010": 36504.45},
                          "efficient": {"2009": 36855.9, "2010": 30960.7}},
               "cost": {
                   "stock": {
                       "total": {"2009": 2972, "2010": 2972},
                       "competed": {"2009": 2972, "2010": 2972},
                       "efficient": {"2009": 2972, "2010": 3700}},
                   "energy": {
                       "total": {"2009": 6601.968, "2010": 6315.443},
                       "competed": {"2009": 6601.968, "2010": 6315.443},
                       "efficient": {"2009": 6601.968, "2010": 5360.489}},
                   "carbon": {
                       "total": {"2009": 1216244.58, "2010": 1204646.90},
                       "competed": {"2009": 1216244.58, "2010": 1204646.90},
                       "efficient": {"2009": 1216244.58, "2010": 1021703.20}}},
               "lifetime": {"baseline": {"2009": 200, "2010": 200},
                            "measure": 10}},
              {"stock": {"total": {"2009": 148, "2010": 148},
                         "competed": {"2009": 148, "2010": 148}},
               "energy": {"total": {"2009": 648.47, "2010": 650.43},
                          "competed": {"2009": 648.47, "2010": 650.43},
                          "efficient": {"2009": 550.0692, "2010": 650.43}},
               "carbon": {"total": {"2009": 36855.9, "2010": 36504.45},
                          "competed": {"2009": 36855.9, "2010": 36504.45},
                          "efficient": {"2009": 31262.24, "2010": 36504.45}},
               "cost": {
                   "stock": {
                       "total": {"2009": 2972, "2010": 2972},
                       "competed": {"2009": 2972, "2010": 2972},
                       "efficient": {"2009": 3700, "2010": 2972}},
                   "energy": {
                       "total": {"2009": 6601.968, "2010": 6315.443},
                       "competed": {"2009": 6601.968, "2010": 6315.443},
                       "efficient": {"2009": 5603.723, "2010": 6315.443}},
                   "carbon": {
                       "total": {"2009": 1216244.58, "2010": 1204646.90},
                       "competed": {"2009": 1216244.58, "2010": 1204646.90},
                       "efficient": {"2009": 1031653.83, "2010": 1204646.90}}},
               "lifetime": {"baseline": {"2009": 200, "2010": 200},
                            "measure": 10}}]

    # Means and sampling Ns for energy, cost, and lifetime that should be
    # generated by "ok_measures_dist" above using the "sample_msegin" dict
    ok_out_dist = [[124.07, 50, 1798.44, 50, 10, 1],
                   [11.13, 50, 379.91, 50, 9.78, 50],
                   [55.74, 50, 6342.07, 50, 10, 1]]

    # Master stock, energy, and cost information that should be generated by
    # "partial_measures" above using the "sample_msegin" dict
    partial_out = [{"stock": {"total": {"2009": 18, "2010": 18},
                              "competed": {"2009": 18, "2010": 18}},
                    "energy": {"total": {"2009": 57.42, "2010": 57.6},
                               "competed": {"2009": 57.42, "2010": 57.6},
                               "efficient": {"2009": 27.5616, "2010": 27.648}},
                    "carbon": {"total": {"2009": 3264.156, "2010": 3235.29},
                               "competed": {"2009": 3264.156, "2010": 3235.29},
                               "efficient": {"2009": 1566.795,
                                             "2010": 1552.939}},
                    "cost": {
                        "stock": {
                            "total": {"2009": 216, "2010": 216},
                            "competed": {"2009": 216, "2010": 216},
                            "efficient": {"2009": 450, "2010": 450}},
                        "energy": {
                            "total": {"2009": 582.2388, "2010": 556.992},
                            "competed": {"2009": 582.2388, "2010": 556.992},
                            "efficient": {"2009": 279.4746, "2010": 267.3562}},
                        "carbon": {
                            "total": {"2009": 107717.16, "2010": 106764.58},
                            "competed": {"2009": 107717.16, "2010": 106764.58},
                            "efficient": {"2009": 51704.24, "2010": 51247}}},
                    "lifetime": {"baseline": {"2009": 120, "2010": 120},
                                 "measure": 10}},
                   {"stock": {"total": {"2009": 52, "2010": 52},
                              "competed": {"2009": 52, "2010": 52}},
                    "energy": {"total": {"2009": 165.88, "2010": 166.4},
                               "competed": {"2009": 165.88, "2010": 166.4},
                               "efficient": {"2009": 67.1176, "2010": 67.328}},
                    "carbon": {"total": {"2009": 9429.785, "2010": 9346.394},
                               "competed": {"2009": 9429.785,
                                            "2010": 9346.394},
                               "efficient": {"2009": 3815.436,
                                             "2010": 3781.695}},
                    "cost": {
                        "stock": {
                            "total": {"2009": 526, "2010": 526},
                            "competed": {"2009": 526, "2010": 526},
                            "efficient": {"2009": 1300, "2010": 1300}},
                        "energy": {
                            "total": {"2009": 1682.023, "2010": 1609.088},
                            "competed": {"2009": 1682.023, "2010": 1609.088},
                            "efficient": {"2009": 680.5725, "2010": 651.0618}},
                        "carbon": {
                            "total": {"2009": 311182.9, "2010": 308431},
                            "competed": {"2009": 311182.9, "2010": 308431},
                            "efficient": {"2009": 125909.39,
                                          "2010": 124795.93}}},
                    "lifetime": {"baseline": {"2009": 80, "2010": 80},
                                 "measure": 10}}]

    # Test for correct output from "ok_measures" input
    def test_mseg_ok(self):
        for idx, measure in enumerate(self.ok_measures):
            # Create an instance of the object based on ok measure info
            measure_instance = run.Measure(**measure)
            # Assert output dict is correct
            dict1 = measure_instance.mseg_find_partition(
                self.sample_msegin,
                self.sample_basein,
                "Technical potential")[0]
            dict2 = self.ok_out[idx]
            self.dict_check(dict1, dict2)

    # Test for correct output from "ok_measures_dist" input
    def test_mseg_ok_distrib(self):
        # Seed random number generator to yield repeatable results
        numpy.random.seed(1234)
        for idx, measure in enumerate(self.ok_measures_dist):
            # Create an instance of the object based on ok_dist measure info
            measure_instance = run.Measure(**measure)
            # Generate lists of energy and cost output values
            test_outputs = measure_instance.mseg_find_partition(
                self.sample_msegin, self.sample_basein,
                "Technical potential")[0]
            test_e = test_outputs["energy"]["efficient"]["2009"]
            test_c = test_outputs["cost"]["stock"]["efficient"]["2009"]
            test_l = test_outputs["lifetime"]["measure"]
            if type(test_l) == float:
                test_l = [test_l]
            # Calculate mean values from output lists for testing
            param_e = round(sum(test_e) / len(test_e), 2)
            param_c = round(sum(test_c) / len(test_c), 2)
            param_l = round(sum(test_l) / len(test_l), 2)
            # Check mean values and length of output lists to ensure correct
            self.assertEqual([param_e, len(test_e), param_c, len(test_c),
                              param_l, len(test_l)],
                             self.ok_out_dist[idx])

    # Test for correct output from "partial_measures" input
    def test_mseg_partial(self):
        for idx, measure in enumerate(self.partial_measures):
            # Create an instance of the object based on partial measure info
            measure_instance = run.Measure(**measure)
            # Assert output dict is correct
            dict1 = measure_instance.mseg_find_partition(
                self.sample_msegin,
                self.sample_basein,
                "Technical potential")[0]
            dict2 = self.partial_out[idx]
            self.dict_check(dict1, dict2)

    # Test for correct output from "blank_measures" input
    def test_mseg_blank(self):
        for idx, measure in enumerate(self.blank_measures):
            # Create an instance of the object based on blank measure info
            measure_instance = run.Measure(**measure)
            # Assert output dict is correct
            with self.assertRaises(KeyError):
                measure_instance.mseg_find_partition(
                    self.sample_msegin,
                    self.sample_basein,
                    "Technical potential")


class PrioritizationMetricsTest(unittest.TestCase, CommonMethods):
    """ Test the operation of the calc_metric_update function to
    verify measure master microsegment inputs yield expected savings
    and prioritization metrics outputs """

    # Set compete measures to True to ensure the full range of measure
    # outputs are calculated
    compete_measures = True

    # Discount rate used for testing
    ok_rate = 0.07

    # Create an "ok" master microsegment input dict with all point
    # values to use in calculating savings and prioritization metrics
    # outputs to be tested
    ok_master_mseg_point = {
        "stock": {
            "total": {"2009": 10, "2010": 20},
            "competed": {"2009": 5, "2010": 10}},
        "energy": {
            "total": {"2009": 20, "2010": 30},
            "competed": {"2009": 10, "2010": 15},
            "efficient": {"2009": 5, "2010": 10}},
        "carbon": {
            "total": {"2009": 200, "2010": 300},
            "competed": {"2009": 100, "2010": 150},
            "efficient": {"2009": 50, "2010": 100}},
        "cost": {
            "stock": {
                "total": {"2009": 10, "2010": 15},
                "competed": {"2009": 10, "2010": 15},
                "efficient": {"2009": 15, "2010": 25}},
            "energy": {
                "total": {"2009": 20, "2010": 35},
                "competed": {"2009": 20, "2010": 35},
                "efficient": {"2009": 10, "2010": 20}},
            "carbon": {
                "total": {"2009": 30, "2010": 40},
                "competed": {"2009": 30, "2010": 40},
                "efficient": {"2009": 25, "2010": 25}}},
        "lifetime": {"baseline": {"2009": 1, "2010": 1},
                     "measure": 2}}

    # Create an "ok" master microsegment input dict with arrays for
    # measure energy use/cost and carbon emitted/cost to use in calculating
    # savings and prioritization metrics outputs to be tested
    ok_master_mseg_dist1 = {
        "stock": {
            "total": {"2009": 10, "2010": 20},
            "competed": {"2009": 5, "2010": 10}},
        "energy": {
            "total": {"2009": 20, "2010": 30},
            "competed": {"2009": 10, "2010": 15},
            "efficient": {
                "2009": numpy.array([1.6, 2.7, 3.1, 6, 5.1]),
                "2010": numpy.array([10.6, 9.5, 8.1, 11, 12.4])}},
        "carbon": {
            "total": {"2009": 200, "2010": 300},
            "competed": {"2009": 100, "2010": 150},
            "efficient": {
                "2009": numpy.array([50.6, 57.7, 58.1, 50, 51.1]),
                "2010": numpy.array([100.6, 108.7, 105.1, 105, 106.1])}},
        "cost": {
            "stock": {
                "total": {"2009": 10, "2010": 10},
                "competed": {"2009": 10, "2010": 15},
                "efficient": {"2009": 15, "2010": 20}},
            "energy": {
                "total": {"2009": 25, "2010": 20},
                "competed": {"2009": 25, "2010": 20},
                "efficient": {
                    "2009": numpy.array([20.1, 18.7, 21.7, 21.2, 22.5]),
                    "2010": numpy.array([9.1, 8.7, 7.7, 11.2, 12.5])}},
            "carbon": {
                "total": {"2009": 30, "2010": 35},
                "competed": {"2009": 30, "2010": 35},
                "efficient": {
                    "2009": numpy.array([25.1, 24.7, 23.7, 31.2, 18.5]),
                    "2010": numpy.array([20.1, 18.7, 21.7, 21.2, 22.5])}}},
        "lifetime": {"baseline": {"2009": 1, "2010": 1},
                     "measure": 2}}

    # Create an "ok" master microsegment input dict with arrays for
    # measure capital cost to use in calculating savings and prioritization
    # metrics outputs to be tested
    ok_master_mseg_dist2 = {
        "stock": {
            "total": {"2009": 10, "2010": 20},
            "competed": {"2009": 5, "2010": 10}},
        "energy": {
            "total": {"2009": 20, "2010": 30},
            "competed": {"2009": 10, "2010": 15},
            "efficient": {"2009": 5, "2010": 10}},
        "carbon": {
            "total": {"2009": 200, "2010": 300},
            "competed": {"2009": 100, "2010": 150},
            "efficient": {"2009": 50, "2010": 100}},
        "cost": {
            "stock": {
                "total": {"2009": 10, "2010": 10},
                "competed": {"2009": 10, "2010": 10},
                "efficient": {
                    "2009": numpy.array([15.1, 12.7, 14.1, 14.2, 15.5]),
                    "2010": numpy.array([20.1, 18.7, 21.7, 19.2, 20.5])}},
            "energy": {
                "total": {"2009": 20, "2010": 35},
                "competed": {"2009": 20, "2010": 35},
                "efficient": {"2009": 10, "2010": 20}},
            "carbon": {
                "total": {"2009": 30, "2010": 40},
                "competed": {"2009": 30, "2010": 40},
                "efficient": {"2009": 25, "2010": 25}}},
        "lifetime": {"baseline": {"2009": 1, "2010": 1},
                     "measure": 2}}

    # Create an "ok" master microsegment input dict with arrays for
    # measure lifetime to use in calculating savings and prioritization
    # metrics outputs to be tested
    ok_master_mseg_dist3 = {
        "stock": {
            "total": {"2009": 10, "2010": 20},
            "competed": {"2009": 5, "2010": 10}},
        "energy": {
            "total": {"2009": 20, "2010": 30},
            "competed": {"2009": 10, "2010": 15},
            "efficient": {"2009": 5, "2010": 10}},
        "carbon": {
            "total": {"2009": 200, "2010": 300},
            "competed": {"2009": 100, "2010": 150},
            "efficient": {"2009": 50, "2010": 100}},
        "cost": {
            "stock": {
                "total": {"2009": 10, "2010": 15},
                "competed": {"2009": 10, "2010": 15},
                "efficient": {"2009": 15, "2010": 25}},
            "energy": {
                "total": {"2009": 20, "2010": 35},
                "competed": {"2009": 20, "2010": 35},
                "efficient": {"2009": 10, "2010": 20}},
            "carbon": {
                "total": {"2009": 30, "2010": 40},
                "competed": {"2009": 30, "2010": 40},
                "efficient": {"2009": 25, "2010": 25}}},
        "lifetime": {"baseline": {"2009": 1, "2010": 1},
                     "measure": numpy.array([0.5, 1.2, 2.1, 2.2, 5.6])}}

    # Create an "ok" master microsegment input dict with arrays for
    # measure capital cost and lifetime to use in calculating savings
    # and prioritization metrics outputs to be tested
    ok_master_mseg_dist4 = {
        "stock": {
            "total": {"2009": 10, "2010": 20},
            "competed": {"2009": 5, "2010": 10}},
        "energy": {
            "total": {"2009": 20, "2010": 30},
            "competed": {"2009": 10, "2010": 15},
            "efficient": {"2009": 5, "2010": 10}},
        "carbon": {
            "total": {"2009": 200, "2010": 300},
            "competed": {"2009": 100, "2010": 150},
            "efficient": {"2009": 50, "2010": 100}},
        "cost": {
            "stock": {
                "total": {"2009": 10, "2010": 10},
                "competed": {"2009": 10, "2010": 10},
                "efficient": {
                    "2009": numpy.array([15.1, 12.7, 14.1, 14.2, 15.5]),
                    "2010": numpy.array([20.1, 18.7, 21.7, 19.2, 20.5])}},
            "energy": {
                "total": {"2009": 20, "2010": 35},
                "competed": {"2009": 20, "2010": 35},
                "efficient": {"2009": 10, "2010": 20}},
            "carbon": {
                "total": {"2009": 30, "2010": 40},
                "competed": {"2009": 30, "2010": 40},
                "efficient": {"2009": 25, "2010": 25}}},
        "lifetime": {"baseline": {"2009": 1, "2010": 1},
                     "measure": numpy.array([0.5, 1.2, 2.1, 2.2, 5.6])}}

    # Savings/prioritization metrics dict keys and values that should be
    # yielded by above point value master microsegment dict input used
    # with point value measure lifetime input
    ok_out_point = {
        "stock": {
            "cost savings (total)": {"2009": -5, "2010": -10},
            "cost savings (added)": {"2009": -5, "2010": -5}},
        "energy": {
            "savings (total)": {"2009": 15, "2010": 20},
            "savings (added)": {"2009": 15, "2010": 5},
            "cost savings (total)": {"2009": 10, "2010": 15},
            "cost savings (added)": {"2009": 10, "2010": 5}},
        "carbon": {
            "savings (total)": {"2009": 150, "2010": 200},
            "savings (added)": {"2009": 150, "2010": 50},
            "cost savings (total)": {"2009": 5, "2010": 15},
            "cost savings (added)": {"2009": 5, "2010": 10}},
        "metrics": {
            "anpv": {
                "stock cost": {
                    "2009": numpy.pmt(0.07, 2, 0.8691589),
                    "2010": numpy.pmt(0.07, 2, 0.9018692)},
                "energy cost": {
                    "2009": numpy.pmt(0.07, 2, 3.616036),
                    "2010": numpy.pmt(0.07, 2, 0.9040091)},
                "carbon cost": {
                    "2009": numpy.pmt(0.07, 2, 1.808018),
                    "2010": numpy.pmt(0.07, 2, 1.808018)}},
            "irr (w/ energy $)": {
                "2009": 3.45, "2010": 3.24},
            "irr (w/ energy and carbon $)": {
                "2009": 4.54, "2010": 5.46},
            "payback (w/ energy $)": {
                "2009": 0.25, "2010": 0.25},
            "payback (w/ energy and carbon $)": {
                "2009": 0.2, "2010": 0.17},
            "cce": {"2009": -0.16, "2010": -1.00},
            "cce (w/ carbon $ benefits)": {
                "2009": -0.49, "2010": -3.00},
            "ccc": {"2009": -0.02, "2010": -0.10},
            "ccc (w/ energy $ benefits)": {
                "2009": -0.08, "2010": -0.20}}}

    # Savings/prioritization metrics dict keys and values that should be
    # yielded by above dist1 master microsegment dict input used with point
    # value measure lifetime input
    ok_out_dist1 = {
        "stock": {
            "cost savings (total)": {"2009": -5, "2010": -10},
            "cost savings (added)": {"2009": -5, "2010": -5}},
        "energy": {
            "savings (total)": {
                "2009": [18.4, 17.3, 16.9, 14.0, 14.9],
                "2010": [19.4, 20.5, 21.9, 19.0, 17.6]},
            "savings (added)": {
                "2009": [18.4, 17.3, 16.9, 14.0, 14.9],
                "2010": [1, 3.2, 5, 5, 2.7]},
            "cost savings (total)": {
                "2009": [4.9, 6.3, 3.3, 3.8, 2.5],
                "2010": [10.9, 11.3, 12.3, 8.8, 7.5]},
            "cost savings (added)": {
                "2009": [4.9, 6.3, 3.3, 3.8, 2.5],
                "2010": [6, 5, 9, 5, 5]}},
        "carbon": {
            "savings (total)": {
                "2009": [149.4, 142.3, 141.9, 150.0, 148.9],
                "2010": [199.4, 191.3, 194.9, 195.0, 193.9]},
            "savings (added)": {
                "2009": [149.4, 142.3, 141.9, 150.0, 148.9],
                "2010": [50, 49, 53, 45, 45]},
            "cost savings (total)": {
                "2009": [4.9, 5.3, 6.3, -1.2, 11.5],
                "2010": [14.9, 16.3, 13.3, 13.8, 12.5]},
            "cost savings (added)": {
                "2009": [4.9, 5.3, 6.3, -1.2, 11.5],
                "2010": [10, 11, 7, 15, 1]}},
        "metrics": {
            "anpv": {
                "stock cost": {
                    "2009": [numpy.pmt(0.07, 2, 0.8691589),
                             numpy.pmt(0.07, 2, 0.8691589),
                             numpy.pmt(0.07, 2, 0.8691589),
                             numpy.pmt(0.07, 2, 0.8691589),
                             numpy.pmt(0.07, 2, 0.8691589)],
                    "2010": [numpy.pmt(0.07, 2, 0.4345794),
                             numpy.pmt(0.07, 2, 0.4345794),
                             numpy.pmt(0.07, 2, 0.4345794),
                             numpy.pmt(0.07, 2, 0.4345794),
                             numpy.pmt(0.07, 2, 0.4345794)]},
                "energy cost": {
                    "2009": [numpy.pmt(0.07, 2, 1.7718578),
                             numpy.pmt(0.07, 2, 2.2781029),
                             numpy.pmt(0.07, 2, 1.1932920),
                             numpy.pmt(0.07, 2, 1.3740938),
                             numpy.pmt(0.07, 2, 0.9040091)],
                    "2010": [numpy.pmt(0.07, 2, 1.0848109),
                             numpy.pmt(0.07, 2, 0.9040091),
                             numpy.pmt(0.07, 2, 1.6272164),
                             numpy.pmt(0.07, 2, 0.9040091),
                             numpy.pmt(0.07, 2, 0.9040091)]},
                "carbon cost": {
                    "2009": [numpy.pmt(0.07, 2, 1.7718578),
                             numpy.pmt(0.07, 2, 1.9164993),
                             numpy.pmt(0.07, 2, 2.2781029),
                             numpy.pmt(0.07, 2, -0.4339244),
                             numpy.pmt(0.07, 2, 4.1584418)],
                    "2010": [numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.9888200),
                             numpy.pmt(0.07, 2, 1.2656127),
                             numpy.pmt(0.07, 2, 2.7120273),
                             numpy.pmt(0.07, 2, 0.1808018)]}},
            "irr (w/ energy $)": {
                "2009": [2.28, 2.61, 1.89, 2.01, 1.69],
                "2010": [2.54, 2.30, 3.23, 2.30, 2.30]},
            "irr (w/ energy and carbon $)": {
                "2009": [3.40, 3.80, 3.36, 1.71, 4.33],
                "2010": [4.76, 4.76, 4.76, 5.61, 2.54]},
            "payback (w/ energy $)": {
                "2009": [0.34, 0.31, 0.38, 0.36, 0.40],
                "2010": [0.31, 0.33, 0.26, 0.33, 0.33]},
            "payback (w/ energy and carbon $)": {
                "2009": [0.25, 0.23, 0.26, 0.40, 0.21],
                "2010": [0.19, 0.19, 0.19, 0.17, 0.31]},
            "cce": {
                "2009": [-0.13, -0.14, -0.14, -0.17, -0.16],
                "2010": [-2.40, -0.75, -0.48, -0.48, -0.89]},
            "cce (w/ carbon $ benefits)": {
                "2009": [-0.40, -0.45, -0.52, -0.09, -0.93],
                "2010": [-12.40, -4.19, -1.88, -3.48, -1.26]},
            "ccc": {
                "2009": [-0.02, -0.02, -0.02, -0.02, -0.02],
                "2010": [-0.05, -0.05, -0.04, -0.05, -0.05]},
            "ccc (w/ energy $ benefits)": {
                "2009": [-0.05, -0.06, -0.04, -0.04, -0.03],
                "2010": [-0.17, -0.15, -0.22, -0.16, -0.16]}}}

    # Savings/prioritization metrics dict keys and values that should be
    # yielded by above dist2 master microsegment dict input used with point
    # value measure lifetime input
    ok_out_dist2 = {
        "stock": {
            "cost savings (total)": {"2009": [-5.1, -2.7, -4.1, -4.2, -5.5],
                                     "2010": [-10.1, -8.7, -11.7, -9.2,
                                              -10.5]},
            "cost savings (added)": {"2009": [-5.1, -2.7, -4.1, -4.2, -5.5],
                                     "2010": [-5.0, -6.0, -7.6, -5.0, -5.0]}},
        "energy": {
            "savings (total)": {"2009": 15, "2010": 20},
            "savings (added)": {"2009": 15, "2010": 5},
            "cost savings (total)": {"2009": 10, "2010": 15},
            "cost savings (added)": {"2009": 10, "2010": 5}},
        "carbon": {
            "savings (total)": {"2009": 150, "2010": 200},
            "savings (added)": {"2009": 150, "2010": 50},
            "cost savings (total)": {"2009": 5, "2010": 15},
            "cost savings (added)": {"2009": 5, "2010": 10}},
        "metrics": {
            "anpv": {
                "stock cost": {
                    "2009": [numpy.pmt(0.07, 2, 0.8491589),
                             numpy.pmt(0.07, 2, 1.329159),
                             numpy.pmt(0.07, 2, 1.049159),
                             numpy.pmt(0.07, 2, 1.029159),
                             numpy.pmt(0.07, 2, 0.7691589)],
                    "2010": [numpy.pmt(0.07, 2, 0.4345794),
                             numpy.pmt(0.07, 2, 0.3345794),
                             numpy.pmt(0.07, 2, 0.1745794),
                             numpy.pmt(0.07, 2, 0.4345794),
                             numpy.pmt(0.07, 2, 0.4345794)]},
                "energy cost": {
                    "2009": [numpy.pmt(0.07, 2, 3.616036),
                             numpy.pmt(0.07, 2, 3.616036),
                             numpy.pmt(0.07, 2, 3.616036),
                             numpy.pmt(0.07, 2, 3.616036),
                             numpy.pmt(0.07, 2, 3.616036)],
                    "2010": [numpy.pmt(0.07, 2, 0.9040091),
                             numpy.pmt(0.07, 2, 0.9040091),
                             numpy.pmt(0.07, 2, 0.9040091),
                             numpy.pmt(0.07, 2, 0.9040091),
                             numpy.pmt(0.07, 2, 0.9040091)]},
                "carbon cost": {
                    "2009": [numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.808018)],
                    "2010": [numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.808018)]}},
            "irr (w/ energy $)":
                {"2009": [3.37, 6.88, 4.34, 4.22, 3.08],
                 "2010": [2.30, 1.80, 1.26, 2.30, 2.30]},
            "irr (w/ energy and carbon $)":
                {"2009": [4.44, 8.82, 5.65, 5.50, 4.08],
                 "2010": [4.54, 3.70, 2.81, 4.54, 4.54]},
            "payback (w/ energy $)":
                {"2009": [0.26, 0.14, 0.21, 0.21, 0.28],
                 "2010": [0.33, 0.40, 0.51, 0.33, 0.33]},
            "payback (w/ energy and carbon $)":
                {"2009": [0.20, 0.11, 0.16, 0.17, 0.22],
                 "2010": [0.20, 0.24, 0.30, 0.20, 0.20]},
            "cce":
                {"2009": [-0.16, -0.25, -0.19, -0.19, -0.14],
                 "2010": [-0.48, -0.37, -0.19, -0.48, -0.48]},
            "cce (w/ carbon $ benefits)":
                {"2009": [-0.49, -0.58, -0.53, -0.52, -0.48],
                 "2010": [-2.48, -2.37, -2.19, -2.48, -2.48]},
            "ccc":
                {"2009": [-0.02, -0.02, -0.02, -0.02, -0.01],
                 "2010": [-0.05, -0.04, -0.02, -0.05, -0.05]},
            "ccc (w/ energy $ benefits)":
                {"2009": [-0.08, -0.09, -0.09, -0.09, -0.08],
                 "2010": [-0.15, -0.14, -0.12, -0.15, -0.15]}}}

    # Savings/prioritization metrics dict keys and values that should be
    # yielded by above point value master microsegment dict input used with
    # array of measure lifetime values input
    ok_out_dist3 = {
        "stock": {
            "cost savings (total)": {"2009": -5, "2010": -10},
            "cost savings (added)": {"2009": -5, "2010": -5}},
        "energy": {
            "savings (total)": {"2009": 15, "2010": 20},
            "savings (added)": {"2009": 15, "2010": 5},
            "cost savings (total)": {"2009": 10, "2010": 15},
            "cost savings (added)": {"2009": 10, "2010": 5}},
        "carbon": {
            "savings (total)": {"2009": 150, "2010": 200},
            "savings (added)": {"2009": 150, "2010": 50},
            "cost savings (total)": {"2009": 5, "2010": 15},
            "cost savings (added)": {"2009": 5, "2010": 10}},
        "metrics": {
            "anpv": {
                "stock cost": {
                    "2009": [numpy.pmt(0.07, 1, -1.0000000),
                             numpy.pmt(0.07, 1, -1.0000000),
                             numpy.pmt(0.07, 2, 0.8691589),
                             numpy.pmt(0.07, 2, 0.8691589),
                             numpy.pmt(0.07, 5, 5.7744225)],
                    "2010": [numpy.pmt(0.07, 1, -0.5000000),
                             numpy.pmt(0.07, 1, -0.5000000),
                             numpy.pmt(0.07, 2, 0.9018692),
                             numpy.pmt(0.07, 2, 0.9018692),
                             numpy.pmt(0.07, 5, 4.5808169)]},
                "energy cost": {
                    "2009": [numpy.pmt(0.07, 1, 1.869159),
                             numpy.pmt(0.07, 1, 1.869159),
                             numpy.pmt(0.07, 2, 3.616036),
                             numpy.pmt(0.07, 2, 3.616036),
                             numpy.pmt(0.07, 5, 8.200395)],
                    "2010": [numpy.pmt(0.07, 1, 0.4672897),
                             numpy.pmt(0.07, 1, 0.4672897),
                             numpy.pmt(0.07, 2, 0.9040091),
                             numpy.pmt(0.07, 2, 0.9040091),
                             numpy.pmt(0.07, 5, 2.0500987)]},
                "carbon cost": {
                    "2009": [numpy.pmt(0.07, 1, 0.9345794),
                             numpy.pmt(0.07, 1, 0.9345794),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 5, 4.1001974)],
                    "2010": [numpy.pmt(0.07, 1, 0.9345794),
                             numpy.pmt(0.07, 1, 0.9345794),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 5, 4.1001974)]}},
            "irr (w/ energy $)":
                {"2009": [1.00, 1.00, 3.45, 3.45, 4.00],
                 "2010": [0.00, 0.00, 3.24, 3.24, 3.99]},
            "irr (w/ energy and carbon $)":
                {"2009": [2.00, 2.00, 4.54, 4.54, 5.00],
                 "2010": [2.00, 2.00, 5.46, 5.46, 6.00]},
            "payback (w/ energy $)":
                {"2009": [0.50, 0.50, 0.25, 0.25, 0.25],
                 "2010": [1.0, 1.0, 0.25, 0.25, 0.25]},
            "payback (w/ energy and carbon $)":
                {"2009": [0.33, 0.33, 0.20, 0.20, 0.20],
                 "2010": [0.33, 0.33, 0.17, 0.17, 0.17]},
            "cce":
                {"2009": [0.36, 0.36, -0.16, -0.16, -0.47],
                 "2010": [1.07, 1.07, -1.00, -1.00, -2.23]},
            "cce (w/ carbon $ benefits)":
                {"2009": [0.02, 0.02, -0.49, -0.49, -0.80],
                 "2010": [-0.93, -0.93, -3.00, -3.00, -4.23]},
            "ccc":
                {"2009": [0.04, 0.04, -0.02, -0.02, -0.05],
                 "2010": [0.11, 0.11, -0.10, -0.10, -0.22]},
            "ccc (w/ energy $ benefits)":
                {"2009": [-0.03, -0.03, -0.08, -0.08, -0.11],
                 "2010": [0.01, 0.01, -0.20, -0.20, -0.32]}}}

    # Savings/prioritization metrics dict keys and values that should be
    # yielded by above dist2 master microsegment dict input used with
    # array of measure lifetime values input
    ok_out_dist4 = {
        "stock": {
            "cost savings (total)": {"2009": [-5.1, -2.7, -4.1, -4.2, -5.5],
                                     "2010": [-10.1, -8.7, -11.7, -9.2,
                                              -10.5]},
            "cost savings (added)": {"2009": [-5.1, -2.7, -4.1, -4.2, -5.5],
                                     "2010": [-5.0, -6.0, -7.6, -5.0, -5.0]}},
        "energy": {
            "savings (total)": {"2009": 15, "2010": 20},
            "savings (added)": {"2009": 15, "2010": 5},
            "cost savings (total)": {"2009": 10, "2010": 15},
            "cost savings (added)": {"2009": 10, "2010": 5}},
        "carbon": {
            "savings (total)": {"2009": 150, "2010": 200},
            "savings (added)": {"2009": 150, "2010": 50},
            "cost savings (total)": {"2009": 5, "2010": 15},
            "cost savings (added)": {"2009": 5, "2010": 10}},
        "metrics": {
            "anpv": {
                "stock cost": {
                    "2009": [numpy.pmt(0.07, 1, -1.02),
                             numpy.pmt(0.07, 1, -0.54),
                             numpy.pmt(0.07, 2, 1.049159),
                             numpy.pmt(0.07, 2, 1.029159),
                             numpy.pmt(0.07, 5, 5.674423)],
                    "2010": [numpy.pmt(0.07, 1, -0.5000000),
                             numpy.pmt(0.07, 1, -0.6000000),
                             numpy.pmt(0.07, 2, 0.1745794),
                             numpy.pmt(0.07, 2, 0.4345794),
                             numpy.pmt(0.07, 5, 2.887211)]},
                "energy cost": {
                    "2009": [numpy.pmt(0.07, 1, 1.869159),
                             numpy.pmt(0.07, 1, 1.869159),
                             numpy.pmt(0.07, 2, 3.616036),
                             numpy.pmt(0.07, 2, 3.616036),
                             numpy.pmt(0.07, 5, 8.200395)],
                    "2010": [numpy.pmt(0.07, 1, 0.4672897),
                             numpy.pmt(0.07, 1, 0.4672897),
                             numpy.pmt(0.07, 2, 0.9040091),
                             numpy.pmt(0.07, 2, 0.9040091),
                             numpy.pmt(0.07, 5, 2.0500987)]},
                "carbon cost": {
                    "2009": [numpy.pmt(0.07, 1, 0.9345794),
                             numpy.pmt(0.07, 1, 0.9345794),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 5, 4.1001974)],
                    "2010": [numpy.pmt(0.07, 1, 0.9345794),
                             numpy.pmt(0.07, 1, 0.9345794),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 2, 1.808018),
                             numpy.pmt(0.07, 5, 4.1001974)]}},
            "irr (w/ energy $)":
                {"2009": [0.96, 2.70, 4.34, 4.22, 3.63],
                 "2010": [0.00, -0.17, 1.26, 2.30, 2.99]},
            "irr (w/ energy and carbon $)":
                {"2009": [1.94, 4.56, 5.65, 5.50, 4.54],
                 "2010": [2.00, 1.50, 2.81, 4.54, 5.00]},
            "payback (w/ energy $)":
                {"2009": [0.51, 0.27, 0.21, 0.21, 0.28],
                 "2010": [999.00, 999.00, 0.51, 0.33, 0.33]},
            "payback (w/ energy and carbon $)":
                {"2009": [0.34, 0.18, 0.16, 0.17, 0.22],
                 "2010": [0.33, 0.40, 0.30, 0.20, 0.20]},
            "cce":
                {"2009": [0.36, 0.19, -0.19, -0.19, -0.46],
                 "2010": [1.07, 1.28, -0.19, -0.48, -1.41]},
            "cce (w/ carbon $ benefits)":
                {"2009": [0.03, -0.14, -0.53, -0.52, -0.79],
                 "2010": [-0.93, -0.72, -2.19, -2.48, -3.41]},
            "ccc":
                {"2009": [0.04, 0.02, -0.02, -0.02, -0.05],
                 "2010": [0.11, 0.13, -0.02, -0.05, -0.14]},
            "ccc (w/ energy $ benefits)":
                {"2009": [-0.03, -0.05, -0.09, -0.09, -0.11],
                 "2010": [0.01, 0.03, -0.12, -0.15, -0.24]}}}

    # Test for correct output from "ok_master_mseg_point"
    def test_metrics_ok_point(self):
        # Create a measure instance to use in the test
        measure_instance = run.Measure(**sample_measure)
        # Set the master microsegment for the measure instance
        # to the "ok_master_mseg_point" dict defined above
        measure_instance.master_mseg = self.ok_master_mseg_point
        # Assert that output dict is correct
        dict1 = measure_instance.calc_metric_update(
            self.ok_rate, self.compete_measures)
        dict2 = self.ok_out_point
        # Check calc_metric_update output (master savings dict)
        self.dict_check(dict1, dict2)

    # Test for correct output from "ok_master_mseg_dist1"
    def test_metrics_ok_distrib1(self):
        # Create a measure instance to use in the test
        measure_instance = run.Measure(**sample_measure)
        # Set the master microsegment for the measure instance
        # to the "ok_master_mseg_dist1" dict defined above
        measure_instance.master_mseg = self.ok_master_mseg_dist1
        # Assert that output dict is correct
        dict1 = measure_instance.calc_metric_update(
            self.ok_rate, self.compete_measures)
        dict2 = self.ok_out_dist1
        # Check calc_metric_update output (master savings dict)
        self.dict_check_list(dict1, dict2)

    # Test for correct output from "ok_master_mseg_dist2"
    def test_metrics_ok_distrib2(self):
        # Create a measure instance to use in the test
        measure_instance = run.Measure(**sample_measure)
        # Set the master microsegment for the measure instance
        # to the "ok_master_mseg_dist2" dict defined above
        measure_instance.master_mseg = self.ok_master_mseg_dist2
        # Assert that output dict is correct
        dict1 = measure_instance.calc_metric_update(
            self.ok_rate, self.compete_measures)
        dict2 = self.ok_out_dist2
        # Check calc_metric_update output (master savings dict)
        self.dict_check_list(dict1, dict2)

    # Test for correct output from "ok_master_mseg_dist3"
    def test_metrics_ok_distrib3(self):
        # Create a measure instance to use in the test
        measure_instance = run.Measure(**sample_measure)
        # Set the master microsegment for the measure instance
        # to the "ok_master_mseg_point" dict defined above
        measure_instance.master_mseg = self.ok_master_mseg_dist3
        # Assert that output dict is correct
        dict1 = measure_instance.calc_metric_update(
            self.ok_rate, self.compete_measures)
        dict2 = self.ok_out_dist3
        # Check calc_metric_update output (master savings dict)
        self.dict_check_list(dict1, dict2)

    # Test for correct output from "ok_master_mseg_dist4"
    def test_metrics_ok_distrib4(self):
        # Create a measure instance to use in the test
        measure_instance = run.Measure(**sample_measure)
        # Set the master microsegment for the measure instance
        # to the "ok_master_mseg_dist2" dict defined above
        measure_instance.master_mseg = self.ok_master_mseg_dist4
        # Assert that output dict is correct
        dict1 = measure_instance.calc_metric_update(
            self.ok_rate, self.compete_measures)
        dict2 = self.ok_out_dist4
        # Check calc_metric_update output (master savings dict)
        self.dict_check_list(dict1, dict2)


class MetricUpdateTest(unittest.TestCase):
    """ Test the operation of the metrics_update function to
    verify cashflow inputs generate expected prioritization metric outputs """

    # Define ok test inputs

    # Test discount rate
    ok_rate = 0.07
    # Test number of units
    ok_num_units = 10
    # Test ok base stock cost
    ok_base_scost = 10
    # Test ok base stock life
    ok_base_life = 3
    # Test ok life of the measure
    ok_product_lifetime = 6.2
    # Test ok capital cost increment
    ok_scostsave = -10
    # Test ok energy savings
    ok_esave = 25
    # Test ok energy cost savings
    ok_ecostsave = 5
    # Test ok carbon savings
    ok_csave = 50
    # Test ok carbon cost savings
    ok_ccostsave = 10
    # Test ok life ratio
    ok_life_ratio = 2

    # Correct metric output values that should be yielded by using "ok"
    # inputs above
    ok_out = numpy.array(
        [numpy.pmt(0.07, 6, -0.1837021), numpy.pmt(0.07, 6, 2.38327),
         numpy.pmt(0.07, 6, 4.76654), 0.62, 1.59, 2, 0.67, 0.02,
         -0.38, 0.01, -0.09])

    # Test for correct outputs given "ok" inputs above
    def test_metric_updates(self):
        # Create a sample measure instance using sample_measure
        measure_instance = run.Measure(**sample_measure)
        # Test that "ok" inputs yield correct output metric values
        # (* Note: outputs should be formatted as numpy arrays)
        numpy.testing.assert_array_almost_equal(
            measure_instance.metric_update(
                self.ok_rate, self.ok_base_scost, self.ok_base_life,
                self.ok_scostsave, self.ok_esave, self.ok_ecostsave,
                self.ok_csave, self.ok_ccostsave, int(self.ok_life_ratio),
                int(self.ok_product_lifetime), self.ok_num_units),
            self.ok_out, decimal=2)


class PaybackTest(unittest.TestCase):
    """ Test the operation of the payback function to
    verify cashflow input generates expected payback output """

    # Define ok test cashflow inputs
    ok_cashflows = [[-10, 1, 1, 1, 1, 5, 7, 8],
                    [-10, 14, 2, 3, 4],
                    [-10, 0, 1, 2],
                    [10, 4, 7, 8, 10]]

    # Correct outputs that should be yielded by above "ok" cashflow inputs
    ok_out = [5.14, 0.71, 999, 0]

    # Test for correct outputs given "ok" input cashflows above
    def test_cashflow_paybacks(self):
        # Create a sample measure instance using sample_measure
        measure_instance = run.Measure(**sample_measure)
        # Test that "ok" input cashflows yield correct output payback values
        for idx, cf in enumerate(self.ok_cashflows):
            self.assertAlmostEqual(measure_instance.payback(cf),
                                   self.ok_out[idx], places=2)


# Offer external code execution (include all lines below this point in all
# test files)
def main():
    # Triggers default behavior of running all test fixtures in the file
    unittest.main()

if __name__ == "__main__":
    main()
