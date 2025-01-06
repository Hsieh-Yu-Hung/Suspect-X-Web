

/* This works
const {onRequest} = require("firebase-functions/v2/https");
exports.helloWorld = onRequest({region: "asia-east1", cors: true},
    (request, response) => {
      response.json({data: {"message": "Hello from Firebase!"}});
    },
);
*/

/* This works
import {onCall} from "firebase-functions/v2/https";

export const helloWorldc = onCall({region: "asia-east1", cors: true},
    (request, response) => {
      return {data: {"message": "Hello from Firebase Callable!"}};
    },
);
*/

/* import module */
import {onCall} from "firebase-functions/v2/https";
import {saveLogger} from "./saveLogs.js";

/* export function */

// 紀錄 logs 到檔案
const saveLogs = onCall({region: "asia-east1", cors: true},
    (request) => {
      const logs = request.data.logs;
      let res = null;
      if (request.data.logType === "info") {
        res = saveLogger.info(logs);
      } else if (request.data.logType === "debug") {
        res = saveLogger.debug(logs);
      } else if (request.data.logType === "error") {
        res = saveLogger.error(logs);
      } else if (request.data.logType === "warn") {
        res = saveLogger.warn(logs);
      }
      return res;
    },
);

export {
  saveLogs,
};

