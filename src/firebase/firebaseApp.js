// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDnAkKgbk7ZwRgYJF9MYdlCoPbSwrQyrZQ",
  authDomain: "accuinbio-suspect-x.firebaseapp.com",
  projectId: "accuinbio-suspect-x",
  storageBucket: "accuinbio-suspect-x.firebasestorage.app",
  messagingSenderId: "1055355904275",
  appId: "1:1055355904275:web:a88a62b0322b4e6e1d3ae6",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Export the Firebase app instance
export default app;
