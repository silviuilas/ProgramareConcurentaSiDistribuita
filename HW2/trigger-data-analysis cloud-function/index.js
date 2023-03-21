const firebase = require('firebase-admin');
const { getFirestore } = require('firebase-admin/firestore');
const parseAsync = require('json2csv');
const uuid = require('uuid');
const fs = require('fs');
const path = require('path');
const os = require('os');

firebase.initializeApp({
  storageBucket: 'voting-app-381012-bucket',
});

const db = getFirestore();

async function getData() {
    const myArray = [];
    const querySnapshot = await db.collectionGroup('vote').get();
    querySnapshot.forEach(doc => {
        myArray.push(doc.data());
    });
    return myArray;
}

exports.triggerDataAnalysis = async () => {

    // gets the documents from the firestore collection
    votes = await getData();

    console.log("Voturi :22");
    console.log(votes);

    // csv field headers
    const fields = [
      'vote_name',
      'timezone',
      'country',
      'city',
      'ip'
    ];

    // get csv output
    const output = await parseAsync.parseAsync(votes, { fields });
    console.log("Parsare date :36");
    console.log(output);

    // generate filename
    const dateTime = new Date().toISOString().replace(/\W/g, "");
    const filename = `votes_${dateTime}.csv`;
    console.log("File name :42");
    console.log(filename);

    const tempLocalFile = path.join(os.tmpdir(), filename);
    console.log("TempLocalFile :46");
    console.log(tempLocalFile);
    
    return new Promise((reject) => {
      //write contents of csv into the temp file
      fs.writeFile(tempLocalFile, output, error => {
        if (error) {
          console.log("Eroare la scrierea in fisierul temporar 50");
          reject(error);
          return;
        }
        const bucket = firebase.storage().bucket();

        // upload the file into the current firebase project default bucket
        bucket
           .upload(tempLocalFile, {
            // Workaround: firebase console not generating token for files
            // uploaded via Firebase Admin SDK
            // https://github.com/firebase/firebase-admin-node/issues/694
            metadata: {
              metadata: {
                firebaseStorageDownloadTokens: uuid.v4(),
              }
            },
            public: true,
          })
          .then(() => { 
            console.log("Upload reusit in bucket :71");
            startDataprocJob("gs://voting-app-381012-bucket/"+filename).then(result => console.lor(result));
          })
          .catch(error => {
            console.log("Eroare upload in bucket :75");
            console.log(error);
            reject(error);
          });
      });
    });
  };

async function startDataprocJob(fileName) {
  const region = 'europe-west1';
  const clusterName = 'voting-app-381012-cluster';
  const projectId = 'voting-app-381012';
  const jobFilePath = 'gs://voting-app-381012-bucket/2023-03-19T15:03:59_72116/vote_count_analysis.py';
  const dataproc = require('@google-cloud/dataproc');

  const jobClient = new dataproc.v1.JobControllerClient({
    apiEndpoint: `${region}-dataproc.googleapis.com`,
    projectId: projectId,
  });
  
  const job = {
    projectId: projectId,
    region: region,
    job: {
      placement: {
        clusterName: clusterName,
      },
      pysparkJob: {
        mainPythonFileUri: jobFilePath,
        args: [
          '--latest_file=' + fileName,
        ],
      },
    },
  };

  const [jobOperation] = await jobClient.submitJobAsOperation(job);
  const [jobResponse] = await jobOperation.promise();
  console.log(jobResponse.driverOutputResourceUri.match('gs://(.*?)/(.*)'));
};

