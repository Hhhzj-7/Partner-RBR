# Partner-RBR

Partner-RBR is a predictor used to identify multi-type RNA-binding residues based on informative protein sequence.



### Dataset

RNA-binding proteins were collected in `train.txt` and `test.txt`,  and the data format was as follows: 

```
# Example
>O42661 (Uniprotid)
MKLVRFLMKLTNETVSIELKNGTIVHGTITSVDMQMNTHLKAVKMTVKGREPVPVETLSIRGNNIRYYILPDSLPLDTLLIDDSTKPKQKKKEVVRGRGRGRGRGTRGRGRGASRGF (Sequence)
000100000000000000010000000000000111100000000000000000000000111001000000000000000000000000000000000000000000000000000 (label for RNA-binding)
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 (label for rRNA-binding)
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 (label for tRNA-binding)
000100000000000000010000000000000111100000000000000000000000111001000000000000000000000000000000000000000000000000000 (label for snRNA-binding)
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 (label for mRNA-binding)
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 (label for SRP-binding)
```



### Feature

Partner-RBR has applied three features: protein sequence feature extracted from MSA, protein embedding representation based on the ProtT5 language model, and protein structural information based on AlphaFold-predicted protein structure.

##### Protein sequence feature based on MSA

- Using [PSI-BLAST](https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.2.26/) to generate PSSM (`uniprotid.prf`)

- Using [PSIPRED](http://bioinf.cs.ucl.ac.uk/psipred) to generate SS (`uniprotid.ss2`)
- Using [SANN](https://github.com/newtonjoo/sann) to generate RSA (`uniprotid.a3`)

##### Protein amino acid embedding based on ProtT5

The protein amino acid embedding (`uniprotid.npy`) was generated by ProtT5 (`./scripts/embedding/ProtT5.ipynb`)

##### Protein structure information based on AlphaFold-predicted structure 

The predicted structure (`AF-uniprotid.pdb`) was generated by AlphaFold protein structure database, which can be found at [AlphaFold DB](https://alphafold.ebi.ac.uk/).

And then, SNB-PSSM (`uniprotif_snb.xlsx`)  was generated from PSSM and predicted-feature by running `./scripts/snb-pssm/main.m`.



### Usage

1. Generate feature profile for each protein. [`./feature_generation/`]

   -- snb_pssm.py  :  Load  `uniprotid_snb.xlsx` and transform it to `uniprotid_snb-pssm.npy`;

   -- Resfea.py  :  Generate sequence feature for each residues in our dataset (`uniprotid_all_fea.npy`)

   -- structure_adj.py  :  Generate  structure feature for each residues  by AlphaFold-predicted structure(`uniprotid_neibor.npy`)

   -- feature_aggreation.py  :  Generate the input of our model， which contains sequence feature, structure feature, and label. And then, we would get the data used in five-fold cross-validtion (`./path to save/train_balance.pkl` and `./path to save/valid.pkl`) and test (`./path to save/test.pickle`).

   >  The source file for protein feature was shown in the `./example/`

2. Train our model. [`./dml/`, `./torch_model/`]

   `./dml/data_loader.py` transform our data (`*.pkl`) to tensor form.

   TextCNN was used to capture latent feature based on our input feature, and its  configuration and code were in `./torch_model/`.

    `./dml/Trainer.py` was used to perform mutual learning, while `./dml/Ind_Trainer` was used to perform independent learning.

   Run `./dml_main.py` to train the model based on our training data, and the trained model was save at `./dml/5cv_ckpt/dml_50/`

3. Predict proteins in public test set by our trained model. [`./predict.py`]


### Contact
If you have any issues or questions about this paper or need assistance with reproducing the results, please contact me.

Zhijian Huang

School of Computer Science and Engineering,

Central South University

Email: zhijianhuang@csu.edu.cn

