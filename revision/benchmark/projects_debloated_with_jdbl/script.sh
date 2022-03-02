PROJECT=https://github.com/alibaba/TProfiler.git

git clone $PROJECT
cd TProfiler
git checkout `git rev-list -n 1 --before="2018-10-15 12:00" master`
mvn clean package
