import time,sys,glob,os
import scipy.io.wavfile as wav
from python_speech_features import mfcc
import numpy as np
import re
from sklearn.ensemble import RandomForestClassifier
#mfccs = []
mfccs=np.array([])
true_labels = []
file_names = []


segments=50 #grains
cepstra=12

magical_threshold=float(sys.argv[2])

#DON'T FORGET, TREELITE SORTS YOUR CATEGORIES ALPHABETICALLY. THUS, YOUR PREDICTOR NEEDS TO HAVE THEM SORTED ALPHABETICALLY AS WELL
labels=sorted(['Affe','Fuchs','Fisch','Kuh','Katze','Löwe','Hahn','Esel','Hund','Schaf','Schwein','Ziege','Reh','Kaninchen','Kamel','Pferd','Huhn','Elefant','Gans','Ente','Girafe','Henne'])
session_id=sys.argv[1]
print("activating predictor")
import treelite_runtime     # runtime module
predictor = treelite_runtime.Predictor('./classifiers/tiere.so', verbose=True)
print("predictor activated")

sounds = glob.glob('./sessions/'+session_id+'/*')
i=0

for audiofile in sounds:
  i=i+1
  start_time=time.time()
  (sampling_rate,signal)=wav.read(audiofile)

  hop=(len(signal)/(segments-1)/sampling_rate)
  features= mfcc(signal,sampling_rate,numcep=cepstra,winstep=hop,nfft=512)

  features.resize(((segments*2)-2,cepstra))
  f=features.flatten()
  batch = treelite_runtime.Batch.from_npy2d(np.array([f]))
  prediction = predictor.predict(batch).flatten()
  two_best=np.argpartition(prediction, -2)[-2:]
  two_best=two_best[np.argsort(prediction[two_best])]
  end_time=time.time()
  difference=prediction[[two_best[1]]]-prediction[[two_best[0]]]

  if difference>magical_threshold:
     print(labels[two_best[1]],labels[two_best[1]] in audiofile,difference,str(end_time-start_time)+' seconds')

