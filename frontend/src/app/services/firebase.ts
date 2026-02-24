import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAnq53lQhN78VMFpxrh_dfzSMD9ajOc4Cw",
  authDomain: "leave-management-system-964ac.firebaseapp.com",
  projectId: "leave-management-system-964ac",
  storageBucket: "leave-management-system-964ac.firebasestorage.app",
  messagingSenderId: "187484122668",
  appId: "1:187484122668:web:b62c880fbfd1cf34886b89"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
