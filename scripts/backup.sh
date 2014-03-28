pg_dump -cO -h localhost -U fufufuu_old_user fufufuu_old > dump.sql
rm -f dump.sql.gz
gzip dump.sql
FILENAME=$(date +"%Y%m%d")
YEAR=$(date +"%Y")
MONTH=$(date +"%m")
aws s3 mv dump.sql.gz s3://fufufuu2/db/$YEAR/$MONTH/$FILENAME.sql.gz
aws s3 sync /var/www/fufufuu2/media/zip s3://fufufuu2/media/zip
