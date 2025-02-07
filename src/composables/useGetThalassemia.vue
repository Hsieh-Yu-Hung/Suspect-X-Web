<script>
export default async function useGetThalassemia(type) {
  return new Promise((resolve, reject) => {
    try {
      return resolve(window.api.getThalassemia(type))
    } catch (err) {
      console.log(err);
      return reject()
    }
  }).then(thalRaw => {
    let thal;
    try {
      thal = thalRaw.map(r => {
        return {
          label: r.name,
          value: r.name,
          chr: r.chr,
          start: r.start,
          end: r.end ? r.end : null,
          gene: r.gene,
          type: r.type,
          common: r.common,
          zygosity: 'hetro',    // Heterozygous, Homozygous
          disease: r.disease,
        }
      });
      return Promise.resolve(thal)
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











