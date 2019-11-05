python query.py -output='Babesiosis.json' -path='output/babesiosis' -max=20 -range='2015-2019' -label='Babesiosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Babesi* OR "Babesia bigemina" OR "Babesia bovis" OR "Babesia bovis" OR "Babesia motasi" OR Piroplasmosis OR "Red water") AND (prevalence OR incidence)'

python query.py -output='Blackleg.json' -path='output/blackleg' -max=20 -range='2015-2019' -label='Blackleg' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Blackleg OR Blackquarter OR "Black leg" OR "Black quarter" OR "Clostridium chauvoei") AND (prevalence OR incidence)'

python query.py -output='Bluetongue.json' -path='output/bluetongue' -max=20 -range='2015-2019' -label='Bluetongue' -search='(Livestock OR ruminants OR sheep OR goats OR ram OR ewe OR cattle OR bull OR cow) AND Ethiopia AND (Bluetongue OR "Blue tongue") AND (prevalence OR incidence)'

python query.py -output='Bovine anaplasmosis.json' -path='output/bovine_anaplasmosis' -max=20 -range='2015-2019' -label='Bovine anaplasmosis' -search='(Livestock OR ruminants OR cattle OR cow OR bull) AND Ethiopia AND (Anaplasm* OR "Bovine anaplasmosis" OR "Anaplasma marginale") AND (prevalence OR incidence)'

python query.py -output='Bovine genital campylobacteriosis.json' -max=100 -range='2015-2019' -label='Bovine genital campylobacteriosis' -search='(Livestock OR ruminants OR cattle OR cow OR bull) AND Ethiopia AND ("Bovine Genital Campylobacteriosis" OR "Campylobacter*" OR "Campylobacter fetus") AND (prevalence OR incidence)'

python query.py -output='Bovine spongiform encephalopathy.json' -max=100 -range='2015-2019' -label='Bovine spongiform encephalopathy' -search='(Livestock OR ruminants OR cattle OR cow OR bull) AND Ethiopia AND ("Bovine Spongiform Encephalopathy" OR "prion disease") AND (prevalence OR incidence")'

python query.py -output='Bovine tuberculosis.json' -max=100 -range='2015-2019' -label='Bovine tuberculosis' -search='(Livestock OR ruminants OR cattle OR cow OR bull) AND Ethiopia AND (Tuberculosis OR "Mycobacterium bovis") AND (prevalence OR incidence)'

python query.py -output='Bovine viral diarrhoea.json' -max=100 -range='2015-2019' -label='Bovine viral diarrhoea' -search='(Livestock OR ruminants OR cattle OR cow OR bull) AND Ethiopia AND (BVD OR "Bovine viral diarr*") AND (prevalence OR incidence)'

python query.py -output='Brucellosis.json' -max=100 -range='2015-2019' -label='Brucellosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Brucell* OR "Brucella abortus" OR "Brucella melitensis" AND (prevalence OR incidence)'

python query.py -output='Caseous lymphadenitis.json' -max=100 -range='2015-2019' -label='Caseous lymphadenitis' -search='(Livestock OR ruminants OR sheep OR goats OR ram OR ewe) AND Ethiopia AND ("Corynebacterium pseudotuberculosis" OR "caseous lymphadenitis") AND (prevalence OR incidence)'

python query.py -output='Chlamydiosis.json' -max=100 -range='2015-2019' -label='Chlamydiosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ewe OR bull OR ram) AND Ethiopia AND (Chlamydi* OR "Chlamydia abortus" OR "Chlamidophila abortus" OR "Enzootic abortion" OR "Ovine Chlamydiosis" OR "Chlamydia pecorum" OR "Chlamydophila pecorum") AND (prevalence OR incidence)'

python query.py -output='Coenurosis.json' -max=100 -range='2015-2019' -label='Coenurosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ewe OR bull OR ram) AND Ethiopia AND (Coenur* OR "Coenurus cerebralis" OR gid OR sturdy) AND (prevalence OR incidence)'

python query.py -output='Co-infections.json' -max=100 -range='2015-2019' -label='Co-infections' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ewe OR bull OR ram) AND Ethiopia AND (co-infection OR "co-infected with" OR co-morbidit*) AND (prevalence OR incidence)'

python query.py -output='Contagious agalactia.json' -max=100 -range='2015-2019' -label='Contagious agalactia' -search='(Livestock OR ruminants OR sheep OR goats OR ewe) AND Ethiopia AND (Mycoplasm* OR "Mycoplasma agalactiae") AND (prevalence OR incidence)'

python query.py -output='Contagious bovine pleuropneumonia (CBPP).json' -max=100 -range='2015-2019' -label='Contagious bovine pleuropneumonia (CBPP)' -search='(Livestock OR ruminants OR cattle OR cow OR bull) AND Ethiopia AND ("Contagious bovine pleuro*" OR CBPP OR Mycoplasma) AND (prevalence OR incidence)'

python query.py -output='Contagious caprine pleuropneumonia (CCPP).json' -max=100 -range='2015-2019' -label='Contagious caprine pleuropneumonia (CCPP)' -search='(Livestock OR ruminants OR goats OR ram OR ewe) AND Ethiopia AND ("Contagious caprine pleuro*" OR CCPP OR Mycoplasma) AND (prevalence OR incidence)'

python query.py -output='Contagious ecthyma (Orf disease).json' -max=100 -range='2015-2019' -label='Contagious ecthyma (Orf disease)' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND ("Contagious ecthyma" OR Orf OR capripox OR "contagious pustular dermatitis") AND (prevalence OR incidence)'

python query.py -output='Cowdriosis.json' -max=100 -range='2015-2019' -label='Cowdriosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Cowdriosis OR Heartwater Or "Ehrichia ruminantium" OR Ehrlichi* OR "tick-borne diseases" OR "haemoparasitic diseases" OR haemoparasites) AND (prevalence OR incidence)'

python query.py -output='Cryptosporidiosis.json' -max=100 -range='2015-2019' -label='Cryptosporidiosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ewe OR calf OR lamb OR kid) AND Ethiopia AND (Cryptosporidi* OR "Cryptosporidium parvum") AND (prevalence OR incidence)'

python query.py -output='Cysticercosis.json' -max=100 -range='2015-2019' -label='Cysticercosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe) AND Ethiopia AND (Cysticerc* OR "Cysticercus bovis" OR "Cysticercus ovis" OR "Taenia saginata" OR "Taenia ovis" OR "Cysticercus tenuicolis" OR "Taenia hydatigena" OR "sheep measles" OR "sheep bladder worm" OR "beef measles") AND (prevalence OR incidence)'

python query.py -output='Dermatophilosis.json' -max=100 -range='2015-2019' -label='Dermatophilosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Dermatophil* OR "Dermatophilus congolensis" OR "tick-borne diseases" OR streptothricosis) AND (prevalence OR incidence)'

python query.py -output='Dermatophytosis.json' -max=100 -range='2015-2019' -label='Dermatophytosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Dermatophytosis OR Microsporum OR "Trichophyton mentagrophytes") AND (prevalence OR incidence)'

python query.py -output='Disease-associated mortality.json' -max=100 -range='2015-2019' -label='Disease-associated mortality' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull OR lamb OR kid) AND Ethiopia AND (Mortality OR "disease-associated mortality" OR "disease mortality") AND (prevalence OR incidence)'

python query.py -output='Echinococcosis.json' -max=100 -range='2015-2019' -label='Echinococcosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Echinococc* OR "Echinococcus granulosus" OR Hydatidosis) AND (prevalence OR incidence)'

python query.py -output='Enterotoxaemia.json' -max=100 -range='2015-2019' -label='Enterotoxaemia' -search='(Livestock OR ruminants OR sheep OR goats OR lamb OR kid) AND Ethiopia AND (enterotoxaemia OR "Clostridium perfringens" OR "pulpy kidney disease" OR "lamb dysentery") AND (prevalence OR incidence)'

python query.py -output='Enzootic bovine leukosis.json' -max=100 -range='2015-2019' -label='Enzootic bovine leukosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND ("enzootic bovine leukosis" OR "bovine leukemia virus") AND (prevalence OR incidence)'

python query.py -output='Fasciolosis.json' -max=100 -range='2015-2019' -label='Fasciolosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Fasciol* OR "Fasciola hepatica" OR "Fasciola gigantica" OR "liver fluke") AND (prevalence OR incidence)'

python query.py -output='Foot and mouth disease (FMD).json' -max=100 -range='2015-2019' -label='Foot and mouth disease (FMD)' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND ("Foot and mouth disease" OR FMD) AND (prevalence OR incidence)'

python query.py -output='Haemorrhagic septicaemia.json' -max=100 -range='2015-2019' -label='Haemorrhagic septicaemia' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND ("Haemorrhagic septicaemia" OR "Pasteurella multocida" OR Pasteurell*) AND (prevalence OR incidence)'

python query.py -output='Infectious bovine rhinotracheitis/infectious pustular vulvovaginitis (IBR/IPV).json' -max=100 -range='2015-2019' -label='Infectious bovine rhinotracheitis/infectious pustular vulvovaginitis (IBR/IPV)' -search='(Livestock OR ruminants OR cattle OR cow) AND Ethiopia AND (IBR OR BHV OR BoHV OR "infectious bovine rhinotracheitis" OR "herpesvirus bovine" OR "pustular vulvovaginitis" OR "bovine rhinotracheitis virus") AND (prevalence OR incidence)'

python query.py -output='Infectious necrotic hepatitis.json' -max=100 -range='2015-2019' -label='Infectious necrotic hepatitis' -search='(Livestock OR ruminants OR sheep OR ewe OR ram) AND Ethiopia AND ("Infectious necrotic hepatitis" OR "black disease" OR "Clostridium novyi") AND (prevalence OR incidence)'

python query.py -output='Infestation with ticks, fleas, lice, mange, mites.json' -max=100 -range='2015-2019' -label='Infestation with ticks, fleas, lice, mange, mites' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR e	we OR bull) AND Ethiopia AND (Ectoparasit* OR lice OR fleas OR mange OR mites OR Demodex OR Rhipicephalus OR Psoroptes OR Hyalomma OR "Melophagus ovinus") AND (prevalence OR incidence)'

python query.py -output='Leptospirosis.json' -max=100 -range='2015-2019' -label='Leptospirosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND Leptospir* AND (prevalence OR incidence)'

python query.py -output='Listeriosis.json' -max=100 -range='2015-2019' -label='Listeriosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ewe) AND Ethiopia AND (Listeri* OR "Listeria monocytogenes") AND (prevalence OR incidence)'

python query.py -output='Lumpy skin disease (LSD).json' -max=100 -range='2015-2019' -label='Lumpy skin disease (LSD)' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND ("Lumpy skin disease" OR LSD) AND (prevalence OR incidence)'

python query.py -output='Malignant catarrhal fever (MCF).json' -max=100 -range='2015-2019' -label='Malignant catarrhal fever (MCF)' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND ("Malignant catarrhal fever" OR MCF OR "ovine herpesvirus") AND (prevalence OR incidence)'

python query.py -output='Nematodiasis.json' -max=100 -range='2015-2019' -label='Nematodiasis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND ("gastrointestinal helminths" OR "gastrointestinal parasites" OR nematode* OR helminth* OR helminthiasis OR "lung worms" OR lungworms OR "lung helminths" OR "lung parasites" OR Strongyloid* OR Ostertagi* OR Haemonch* OR Trichostrongyl* OR Nematodirus OR Parmphistomum OR Oesophagostomum OR Dictyocaulus OR Protostrongylus) AND (prevalence OR incidence)'

python query.py -output='Neosporosis.json' -max=100 -range='2015-2019' -label='Neosporosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Neosporosis OR "Neospora caninum") AND (prevalence OR incidence)'

python query.py -output='Ovine epididymitis.json' -max=100 -range='2015-2019' -label='Ovine epididymitis' -search='(Livestock OR ruminants OR sheep OR ram) AND Ethiopia AND ("Ovine epididymitis" OR "Brucella ovis") AND (prevalence OR incidence)'

python query.py -output='Paratuberculosis.json' -max=100 -range='2015-2019' -label='Paratuberculosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Paratuberculosis OR "Johne’s disease" OR "Mycobacterium avium") AND (prevalence OR incidence)'

python query.py -output='Pasteurellosis.json' -max=100 -range='2015-2019' -label='Pasteurellosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Pasteurell* OR Manhemi*) AND (prevalence OR incidence)'

python query.py -output='Peste des petits ruminants (PPR).json' -max=100 -range='2015-2019' -label='Peste des petits ruminants (PPR)' -search='(Livestock OR ruminants OR sheep OR goats OR ram OR ewe) AND Ethiopia AND (PPR OR "Peste des petits ruminants") AND (prevalence OR incidence)'

python query.py -output='Q fever (Coxiellosis).json' -max=100 -range='2015-2019' -label='Q fever (Coxiellosis)' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Coxiell* OR "Q fever" OR "Coxiella burnetii") AND (prevalence OR incidence)'

python query.py -output='Rabies.json' -max=100 -range='2015-2019' -label='Rabies' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND Rabies AND (prevalence OR incidence)'

python query.py -output='Salmonellosis.json' -max=100 -range='2015-2019' -label='Salmonellosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Salmonell* OR "Salmonella abortusovis" OR "Salmonella typhimurium") AND (prevalence OR incidence)'

python query.py -output='Sarcocystosis.json' -max=100 -range='2015-2019' -label='Sarcocystosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Sarcocyst* OR sarcosporidiasis) AND (prevalence OR incidence)'

python query.py -output='Schmallenberg.json' -max=100 -range='2015-2019' -label='Schmallenberg' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND Schmallenberg AND (prevalence OR incidence)'

python query.py -output='Scrapie.json' -max=100 -range='2015-2019' -label='Scrapie' -search='(Livestock OR ruminants OR sheep OR goats OR ram OR ewe) AND Ethiopia AND (Scrapie OR "prion disease") AND (prevalence OR incidence)'

python query.py -output='Sheep and goat pox.json' -max=100 -range='2015-2019' -label='Sheep and goat pox' -search='(Livestock OR ruminants OR sheep OR goats OR ram OR ewe) AND Ethiopia AND ("sheep and goat pox" OR "pox" OR "Capripox virus") AND (prevalence OR incidence)'

python query.py -output='Small ruminant lentivirus infections.json' -max=100 -range='2015-2019' -label='Small ruminant lentivirus infections' -search='(Livestock OR ruminants OR sheep OR goats OR ram OR ewe) AND Ethiopia AND ("Maedi-Visna" OR Maedi OR "ovine progressive interstitial pneumonia" OR "Infectious arthritis/encephalitis" OR "small ruminant lentivirus") AND (prevalence OR incidence)'

python query.py -output='Small ruminant Tuberculosis.json' -max=100 -range='2015-2019' -label='Small ruminant Tuberculosis' -search='(Livestock OR ruminants OR sheep OR goats OR ram OR ewe) AND Ethiopia AND (Tuberculosis OR mycobacterium) AND (prevalence OR incidence)'

python query.py -output='Theileriosis.json' -max=100 -range='2015-2019' -label='Theileriosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Theileri* OR "Theileria mutans" OR "Theileria orientalis" OR "Theileria velifera" OR "Theileria ovis" OR "tick-borne diaseases" OR "haemoparasitic diseases" OR haemoparasites OR Piroplasmosis) AND (prevalence OR incidence)'

python query.py -output='Toxoplasmosis.json' -max=100 -range='2015-2019' -label='Toxoplasmosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Toxoplasm* OR "Toxoplasma gondii") AND Ethiopia AND (prevalence OR incidence)'

python query.py -output='Trichomonosis.json' -max=100 -range='2015-2019' -label='Trichomonosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ewe) AND Ethiopia AND (Trichomon* OR "Trichomonas foetus") AND Ethiopia AND (prevalence OR incidence)'

python query.py -output='Trypanosomosis.json' -max=100 -range='2015-2019' -label='Trypanosomosis' -search='(Livestock OR ruminants OR sheep OR goats OR cattle OR cow OR ram OR ewe OR bull) AND Ethiopia AND (Trypanosom* OR "Trypanosoma vivax" OR "Trypanosoma brucei" OR "Trypanosoma congolense") AND Ethiopia AND (prevalence OR incidence)'

