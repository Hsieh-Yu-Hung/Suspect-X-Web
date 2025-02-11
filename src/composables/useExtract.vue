<script>
import moment from "moment";

export default function extract(subjectFile) {
  const genderDefined = {
    '女': "female",
    '男': "male",
  };

  function dateTrandfer(date) {
    const year = String(Number(date.split('/')[0]) + 1911);
    const month = String(date.split('/')[1]);
    const day = String(date.split('/')[2]);

    return moment(year + month + day)
  };

  return new Promise((resolve, reject) => {
    try {
      return resolve(window.api.extractSubjectFile(subjectFile))
    } catch (err) {
      console.log(err);
      return reject()
    }
  }).then(subjectInfoAll => {
    let subjectInfo = {};
    try {
      subjectInfoAll.forEach((s) => {
        let id = s.orderingDate.replace(/\//g, '') + s.serialId;
        subjectInfo[id] = {
          name: s.name ? String(s.name) : "",
          birth: s.dob ? moment(dateTrandfer(s.dob)).format("YYYY/MM/DD") : "",
          gender: s.gender
            ? s.gender in genderDefined
              ? genderDefined[s.gender]
              : ""
            : "",
          type: "",
          idNumber: s.idNumber ? String(s.idNumber) : "",
          collectingDate: s.collectionDate ? moment(dateTrandfer(s.collectionDate)).format("YYYY/MM/DD") : "",
          receivedDate: s.orderingDate ? moment(dateTrandfer(s.orderingDate)).format("YYYY/MM/DD") : "",
          edit: true
        }
      });
      return Promise.resolve(subjectInfo)
    } catch (err) {
      console.log(err);
      return Promise.reject()
    }
  }).catch(err => {
    console.log(err);
    return Promise.reject()
  })
}
</script>