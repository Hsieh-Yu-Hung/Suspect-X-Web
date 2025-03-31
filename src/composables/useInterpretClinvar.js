/* 定義一個 KeyWord 物件 */
class KeyWord {
  constructor(value, label) {
    // 如果 value 為空，則設定 value 為空字串
    if (value) {
      this.value = value;
    } else {
      this.value = '';
    }
    // 如果 label 為空，則設定 label 為空字串
    if (label) {
      this.label = label;
    } else {
      this.label = '';
    }
  }
}

/* 定義一個 VAR 物件繼承自 KeyWord 物件 */
class VAR extends KeyWord {
  constructor(value, label) {
    super(value, label);
  }
}

/* 定義一個 CLINSIG 物件繼承自 KeyWord 物件 */
class CLINSIG extends KeyWord {
  constructor(value, label, severity_level) {
    super(value, label);
    this.severity_level = severity_level;

    // 設定顏色
    this.color = severity_level > 7 ? 'red-7'
               : severity_level > 5 ? 'orange-7'
               : severity_level >= 3 ? 'grey-7'
               : 'green-4';
  }
}

/* 定義一個 CONSEQUENCE 物件繼承自 KeyWord 物件 */
class CONSEQUENCE extends KeyWord {
  constructor(value, label) {
    super(value, label);
  }
}

/* 定義 Variant Class 源自 Tracy 的結果 */
const Variant = {
  SNV: new VAR("SNV", "Single Nucleotide Variant"),
  Deletion: new VAR("Deletion", "Deletion"),
  Insertion: new VAR("Insertion", "Insertion"),
  Complex: new VAR("Complex", "Complex"),
  unknown: new VAR("unknown", "unknown"),
}

/* 定義 Clinical Significance 源自 2025/03/28 Clinvar 版本 */
const ClinicalSignificance = {
  Pathogenic: new CLINSIG("Pathogenic", "Pathogenic", 9),
  Likely_pathogenic: new CLINSIG("Likely pathogenic", "Likely pathogenic", 8),
  Benign: new CLINSIG("Benign", "Benign", 1),
  Likely_benign: new CLINSIG("Likely benign", "Likely benign", 2),
  Conflicting_classifications_of_pathogenicity: new CLINSIG("Conflicting classifications of pathogenicity", "Conflicting classifications of pathogenicity", 7),
  Uncertain_significance: new CLINSIG("Uncertain significance", "Uncertain significance", 6),
  no_classification_for_the_single_variant: new CLINSIG("no classification for the single variant", "no classification for the single variant", 5),
  other: new CLINSIG("other", "other", 3),
  not_provided: new CLINSIG("not provided", "not provided", 4),
}

/* 定義 Consequence 源自 2025/03/28 Clinvar 版本 */
const Consequence = {
  start_lost: new CONSEQUENCE("start_lost", "Start Loss"),
  splice_donor_variant: new CONSEQUENCE("splice_donor_variant", "Splice Donor"),
  splice_donor_5th_base_variant: new CONSEQUENCE("splice_donor_5th_base_variant", "Splice Donor 5th Base"),
  intron_variant: new CONSEQUENCE("intron_variant", "Intron"),
  stop_gained: new CONSEQUENCE("stop_gained", "Stop Gained"),
  frameshift_variant: new CONSEQUENCE("frameshift_variant", "Frame Shift"),
  splice_acceptor_variant: new CONSEQUENCE("splice_acceptor_variant", "Splice Acceptor"),
  coding_sequence_variant: new CONSEQUENCE("coding_sequence_variant", "Coding Sequence"),
  three_prime_UTR_variant: new CONSEQUENCE("3_prime_UTR_variant", "3_prime UTR"),
  splice_donor_region_variant: new CONSEQUENCE("splice_donor_region_variant", "Splice Donor Region"),
  inframe_deletion: new CONSEQUENCE("inframe_deletion", "Inframe Deletion"),
  inframe_insertion: new CONSEQUENCE("inframe_insertion", "Inframe Insertion"),
  splice_region_variant: new CONSEQUENCE("splice_region_variant", "Splice Region"),
  five_prime_UTR_variant: new CONSEQUENCE("5_prime_UTR_variant", "5_prime UTR"),
  stop_lost: new CONSEQUENCE("stop_lost", "Stop Loss"),
  splice_polypyrimidine_tract_variant: new CONSEQUENCE("splice_polypyrimidine_tract_variant", "Splice Polypyrimidine Tract"),
  stop_retained_variant: new CONSEQUENCE("stop_retained_variant", "Stop Retained"),
  synonymous_variant: new CONSEQUENCE("synonymous_variant", "Synonymous"),
  missense_variant: new CONSEQUENCE("missense_variant", "Missense"),
  transcript_ablation: new CONSEQUENCE("transcript_ablation", "Transcript Ablation"),
}

export { Variant, ClinicalSignificance, Consequence };