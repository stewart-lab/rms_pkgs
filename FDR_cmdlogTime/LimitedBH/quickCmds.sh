sort -k8,8n -k6,6n rnd.deSeq2_fdr.tsv \
| perl -nle 'if (1 == ++$k){print}else{@f=split /\t/; $fdr=pop @f; if ($f[6] ne ""){print join("\t", @f, sprintf("%.2f", $fdr))}}' | head
perl -e 'print "\n\n"'
sort -k8,8n -k6,6n rnd.deSeq2_fdr_goi.tsv \
| perl -nle 'if (1 == ++$k){print}else{@f=split /\t/; $fdr=pop @f; if ($f[6] ne ""){print join("\t", @f, sprintf("%.2f", $fdr))}}' | head
perl -e 'print "\n\n"'
sort -k8,8n -k6,6n rnd.deSeq2_fdr_goir.tsv \
| perl -nle 'if (1 == ++$k){print}else{@f=split /\t/; $fdr=pop @f; if ($f[6] ne ""){print join("\t", @f, sprintf("%.2f", $fdr))}}' | head
