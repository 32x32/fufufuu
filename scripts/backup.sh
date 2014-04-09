pg_dump -cO -h localhost -U fufufuu_user fufufuu > dump.sql
rm -f dump.sql.gz
gzip dump.sql
FILENAME=$(date +"%Y%m%d")
YEAR=$(date +"%Y")
MONTH=$(date +"%m")
aws s3 mv dump.sql.gz s3://fufufuu/db/$YEAR/$MONTH/$FILENAME.sql.gz
aws s3 sync --delete /var/www/fufufuu/media/manga-archive s3://fufufuu/media/manga-archive
