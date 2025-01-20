export { default as firebaseApp } from "./firebaseApp";
export * from "./firebaseAuth";
export * from "./firebaseStorage";
export * from "./firebaseFunction";
export * from "./firebaseDatabase";

// 如果是開發環境，則執行 onDevelopment()
import onDevelopment from "./onDevelopment";
if (process.env.VUE_APP_FILE_ENV === "development") {
  onDevelopment();
}

