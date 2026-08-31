import { initializeApp } from "firebase/app";

import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
} from "firebase/auth";

import { getFirestore } from "firebase/firestore";

/* =========================================================
   FIREBASE CONFIG
========================================================= */

const firebaseConfig = {
  apiKey: "AIzaSyC1g5PRIgWDR5qXCYBP4u_H5DkuaM_Etgw",
  authDomain: "ip-sakti-sahayak.firebaseapp.com",
  projectId: "ip-sakti-sahayak",
  storageBucket: "ip-sakti-sahayak.firebasestorage.app",
  messagingSenderId: "758398574407",
  appId: "1:758398574407:web:4a9d9ffb98097336e73662",
  measurementId: "G-DPW6LR21QS",
};

/* =========================================================
   INITIALIZE FIREBASE
========================================================= */

const app = initializeApp(firebaseConfig);

/* =========================================================
   FIREBASE AUTHENTICATION
========================================================= */

export const auth = getAuth(app);

/* =========================================================
   GOOGLE AUTHENTICATION
========================================================= */

export const googleProvider =
  new GoogleAuthProvider();

/* =========================================================
   FIRESTORE DATABASE
========================================================= */

export const db = getFirestore(app);

/* =========================================================
   LOGIN
========================================================= */

export const loginWithGoogle = () =>
  signInWithPopup(auth, googleProvider);

/* =========================================================
   LOGOUT
========================================================= */

export const logoutUser = () =>
  signOut(auth);

