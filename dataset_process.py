from data_utils import interpolate_

#traj_data (dict): key - mmsi 
#====================================== 
LAT,LON,SOG,COG,HEAD, NAV,TIMESTAMP,MMSI = range(8) 
print("Cutting discontiguous voyages into contiguous ones...")
count = 0
voyages = dict()
INTERVAL_MAX = 2*3600 # 2h
for mmsi in list(traj_data.keys()):
    v = traj_data[mmsi]["traj"]
    if v.shape[0]>0:
        # Intervals between successive messages in a track
        intervals = v[1:,TIMESTAMP] - v[:-1,TIMESTAMP]
        idx = np.where(intervals > INTERVAL_MAX)[0]
        if len(idx) == 0:
            voyages[count] = v
            count += 1
        else:
            tmp = np.split(v,idx+1)
            for t in tmp:
                voyages[count] = t
                count += 1

#======================================
print("Removing AIS track whose length is smaller than 50 or those last less than 4h...")

for k in list(voyages.keys()):
    duration = voyages[k][-1,TIMESTAMP] - voyages[k][0,TIMESTAMP]
    if (len(voyages[k]) < 20) or (duration < 4*3600):
        voyages.pop(k, None)

#======================================
# Sampling, resolution = 5 min
print('Sampling...')
Vs = dict()
count = 0
resolution = 5*60
for k in tqdm(list(voyages.keys())):
    v = voyages[k]
    sampling_track = np.empty((0, 8))
    for t in range(int(v[0,TIMESTAMP]), int(v[-1,TIMESTAMP]), resolution): # 5 min
        tmp = interpolate_(t,v)
        if tmp is not None:
            sampling_track = np.vstack([sampling_track, tmp])
        else:
            sampling_track = None
            break
    if sampling_track is not None:
        Vs[count] = sampling_track
        count += 1

#======================================
print('Re-Splitting...')
DURATION_MAX = 12#h
one_hour = 12
Data = dict()
count = 0
for k in tqdm(list(Vs.keys())): 
    v = Vs[k]
    # Split AIS track into small tracks whose duration <= 1 day
    idx = np.arange(0, len(v), one_hour*DURATION_MAX)[1:]
    tmp = np.split(v,idx)
    for subtrack in tmp:
        # only use tracks whose duration >= 4 hours
        if len(subtrack) >= one_hour*DURATION_MAX:
            Data[count] = subtrack
            count += 1
print(len(Data))
