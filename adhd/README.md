# ADHD Data
- ADHD
```shell
{'cohort1-control': {'mean': 2.2034, 'std_error': 0.0377}, 'cohort1-adhd': {'mean': 2.1684, 'std_error': 0.0277}, 'cohort2-control': {'mean': 2.4444, 'std_error': 0.1062}, 'cohort2-adhd': {'mean': 2.2353, 'std_error': 0.0666}}

```

- Traditional
```shell
{'cohort1-control': {'mean': 11.1448, 'std_error': 0.1706}, 'cohort1-adhd': {'mean': 10.7509, 'std_error': 0.1835}, 'cohort2-control': {'mean': 7.3333, 'std_error': 0.2461}, 'cohort2-adhd': {'mean': 6.4412, 'std_error': 0.3552}}
```

- Time
```shell
Distance matrices for /media/shovon/Multimedia/dfc/adhd/data/DFC_adhd_filt_adhd2.mat are generated in 829.2459 seconds - 13 subjects
Distance matrices for /media/shovon/Multimedia/dfc/adhd/data/DFC_adhd_filt_adhd1.mat are generated in 11325.7062 seconds - 208 subjects
Distance matrices for /media/shovon/Multimedia/dfc/adhd/data/DFC_adhd_filt_adhd3.mat are generated in 8014.1631 seconds - 136 subjects
Distance matrices for /media/shovon/Multimedia/dfc/adhd/data/DFC_adhd_filt_controls.mat are generated in 30981.4791 seconds - 573 subjects

```
- T and p values for tda TR 2, TR 2.5
```shell
Pipeline: tda
Cohort 1 => control: 290 subjects, ADHD: 285 subjects
Cohort 2 => control: 189 subjects, ADHD: 68 subjects
Cohort 1 (TR=2s):
t-statistic: 0.7493767923512027
p-value: 0.45396370539190223
Significant difference: False
Cohort 2 (TR=2.5s):
t-statistic: 1.668262210213111
p-value: 0.09649357532573855
Significant difference: False
Pipeline: traditional
Cohort 1 => control: 290 subjects, ADHD: 285 subjects
Cohort 2 => control: 189 subjects, ADHD: 68 subjects
Cohort 1 (TR=2s):
t-statistic: 1.572242829928382
p-value: 0.11644987804646008
Significant difference: False
Cohort 2 (TR=2.5s):
t-statistic: 2.0646432077939783
p-value: 0.04086190789178069
Significant difference: True
```
- Data exploration
```shell
(171, 190) - Means 
#timepoints = 171
#ROIs = 190
```
- From dataset readme
```shell
ADHD database has the following groups (930 subjects):
0 = control (573 subs)
1 = ADHD-1 / ADHD-Combined (208 subs)
2 = ADHD-2 / ADHD-Hyperactive/Impulsive (13 subs)
3 = ADHD-3 / ADHD-Inattentive (136 subs)


TR = Between 1.5 and 2.5 seconds (varies across institutes, see TR.xlsx)

Template used:
CC200



ts_adhd_dc.mat:
cc200 ROI timeseries (deconvolved). Each subject #timepoints x #ROIs

deconv_parameters_adhd.mat:
Parameters obtained when deconvolution (Wu et al.) was performed on ROI timeseries

ts_adhd_filt.mat:
cc200 ROI timeseries (bandpass filtered 0.01-0.1Hz). Each subject #timepoints x #ROIs

ts_adhd_nonfiltered_subjectwise.zip:
Contains timeseries data (cc200) for each subject organized in different folders based on institutions (data is preprocessed but Not filtered or deconvolved)

sfc_adhd_dc.mat:
Static FC using deconvolved data (#ROI x #ROI x #subjects)

sfc_adhd_filt.mat:
Static FC using filtered data (#ROI x #ROI x #subjects)

```





# Mishra TDA Data

### File structure
```shell
tree -L 3 -I venv -I README.md -I requirements.txt
.
├── origsubjects_to_use
│   ├── All_binary
│   │   ├── sub-MBAR10018_conn_mat_binary_data_10082024.mat
│   │   ├── ...
│   │   └── sub-MBAR40056_conn_mat_binary_data_10082024.mat
│   ├── All_fibre_count
│   │   ├── sub-MBAR10018_fiber_count_data_10082024.mat
│   │   ├── ...
│   │   └── sub-MBAR40056_fiber_count_data_10082024.mat
│   └── All_fn_times_fa
│       ├── sub-MBAR10018_fn_times_fa_data_10082024.mat
│       ├── ...
│       └── sub-MBAR40056_fn_times_fa_data_10082024.mat
└── RISHSubjects_to_use
    ├── All_binary
    │   ├── sub-MBAR10018_conn_mat_binary_data_10082024.mat
    │   ├── ...
    │   └── sub-MBAR40056_conn_mat_binary_data_10082024.mat
    ├── All_fibre_count
    │   ├── sub-MBAR10018_fiber_count_data_10082024.mat
    │   ├── ...
    │   └── sub-MBAR40056_fiber_count_data_10082024.mat
    └── All_fn_times_fa
        ├── sub-MBAR10018_fn_times_fa_data_10082024.mat
        ├── ...
        └── sub-MBAR40056_fn_times_fa_data_10082024.mat
9 directories, 666 files
```

### Data description
As you will see, there are 2 folders:

- “Orig subjects to use” in which each subject has 3 different types of adjacency matrices: binary, fiber count, fiber count*FA.
- “RISH subjects to use” where we harmonized the dMRI data across the 4 sites using RISH and computed the same adjacency matrices. (RISH paper is here: https://pubmed.ncbi.nlm.nih.gov/35788044/)
- You will notice that RISH and ORIG have different dimensions. This is because RISH up samples the data during the harmonization process. But they are both registered to the same AAL atlas. However, due to the higher resolution and further dilation of the nodal voxels, we lose ROIs with smaller voxels in ORIG, but they are retained in RISH.
- Site ID can be found in the nomenclature: *100** represents site 1 while site *400** represents site 4. For example, sub-MBAR30034_fn_times_fa_data_10082024.mat is from site-3 and sub-MBAR20048_fn_times_fa_data_10082024.mat is from site-2. Also, sub-MBAR10034_fn_times_fa_data_10082024.mat and sub-MBAR30034_fn_times_fa_data_10082024.mat correspond to data from same subject, scanned at sites 1 and 3 respectively.

### Tasks
- [x] Initial check of the matfiles
- [x] Convert the matfiles to distance matrices
- [ ] Paired ANOVA of connectivity matrices across the 4 sites for both orig and RISH. This should give some connections that are significantly different between sites for the same subject. The differences must be larger for orig compared to RISH
- [ ] Paired ANOVA of TDA metrics across the 4 sites for both orig and RISH. This should give fewer connections that are significantly different between sites for the same subject as compared to #1 above.
- [ ] A paired multi-way 4x2x2 ANOVA can also be done to see the effect of site (4 sites), effect of harmonization (orig vs RISH) and effect of pipeline (traditional vs TDA)
