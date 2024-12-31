import app from "./firebaseApp";
import { getFunctions } from "firebase/functions";

const functions = getFunctions(app);

export default functions;
