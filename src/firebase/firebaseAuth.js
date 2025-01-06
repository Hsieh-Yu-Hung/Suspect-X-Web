import app from "./firebaseApp";
import { getAuth, createUserWithEmailAndPassword } from "firebase/auth";

const auth = getAuth(app);

// 建立註冊函式
export const create_User_Account = (email, password) => {
  return createUserWithEmailAndPassword(auth, email, password);
};
