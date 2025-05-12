import { collection, getDocs } from 'firebase/firestore';
import { dataset_list, Database } from '@/firebase/firebaseDatabase';

// 取得測試資料集
const getTestingData = async (dataset_class) => {
  let testing_data = [];
  const search_path = `${dataset_list.testing_data}`;
  const collectionRef = collection(Database, search_path);
  const querySnapshot = await getDocs(collectionRef);
  querySnapshot.forEach(async (document) => {
    const doc_data = document.data();
    if (doc_data.dataset_class === dataset_class) {
      testing_data.push(doc_data);
    }
  });
  return testing_data;
}

export default getTestingData;