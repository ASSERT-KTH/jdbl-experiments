# Results of debloating the benchmark projects of Bruce et al. (Table 3 of their paper)

We successfully debloated 16/25 projects with JDBL.

From the 9 projects that we didn't debloated with JDBL:
- 6 projects are multi-module 
- 2 projects didn't build due to test errors
- 1 project we didn't find the original project repository

| **Project**                                                                                  | **Commit SHA** | **JShrink Reduction** | **JDBL Reduction**          | **JShrink Test Failures** | **JDBL Test Failures** | **JDBL Execution Time (s)** | **Compile Scope Dependencies** | **JDBL Removed Classes** | **JDBL Removed Methods in Used Classes** | **JDBL Debloating Result**                          |
|----------------------------------------------------------------------------------------------|----------------|-----------------------|-----------------------------|---------------------------|------------------------|-----------------------------|--------------------------------|--------------------------|------------------------------------------|-----------------------------------------------------|
| [jvm-tools](https://github.com/aragozin/jvm-tools)                                           | `65ab61f`      | --                    | --                          | --                        | --                     | --                          | --                             | --                       | --                                       | This project is multi-module                        |
| [Bukkit](https://github.com/Bukkit/Bukkit)                                                   | `f210234e`     | 18.5%                 | 1884032/4896046 (61.51%)    | 0                         | 0                      | 143.583                     | 7                              | 2042                     | 940                                      | Success                                             |                                                                                                                               |
| [qart4j](https://github.com/dieforfree/qart4j)                                               | `70b9abb`      | 46.8%                 | 783399/1913880 (59.07%)     | 0                         | 0                      | 72.97                       | 6                              | 698                      | 0                                        | Success                                             |
| [dubbokeeper](https://github.com/dubboclub/dubbokeeper)                                      | `1e24d79`      | --                    | --                          | --                        | --                     | --                          | --                             | --                       | --                                       | This project is multi-module                        |
| [frontend-maven-plugin](https://github.com/eirslett/frontend-maven-plugin)                   | `62376ae`      | --                    | --                          | --                        | --                     | --                          | --                             | --                       | --                                       | This project is multi-module                        |
| [gson](https://github.com/google/gson)                                                       | `27c93352`     | 5.5%                  | 237488/241475 (1.65%)       | 0                         | 0                      | 63.172                      | 0                              | 3                        | 48                                       | Success                                             |
| [DiskLruCache](https://github.com/JakeWharton/DiskLruCache)                                  | `3e016356`     | 1.7%                  | 22585/23266 (2.92%)         | 0                         | 0                      | 66.237                      | 4                              | 132                      | 472                                      | Success                                             |
| [retrofit1-okhttp3-client](https://github.com/JakeWharton/retrofit1-okhttp3-client)          | `9993fdc`      | 11.5%                 | 574733/736167 (21.93%)      | 0                         | 0                      | 77.848                      | 0                              | 0                        | 2                                        | Success                                             |
| [RxRelay](https://github.com/JakeWharton/RxRelay)                                            | `82db28c`      | 17.5%                 | 2116890/2350951 (9.96%)     | 0                         | 0                      | 109.266                     | 2                              | 162                      | 833                                      | Success                                             |
| [RxReplayingShare](https://github.com/JakeWharton/RxReplayingShare)                          | `fbedd63`      | 22.1%                 | 2011178/2168441 (7.25%)     | 0                         | 0                      | 95.089                      | 2                              | 118                      | 686                                      | Success                                             |
| [junit4](https://github.com/junit-team/junit4)                                               | `67d424b2`     | 6.8%                  | 397431/416838 (4.66%)       | 13                        | 0                      | 80.802                      | 1                              | 28                       | 83                                       | Success                                             |
| [http-request](https://github.com/kevinsawicki/http-request)                                 | `2d62a3e`      | 6.6%                  | 34214/36978 (7.47%)         | 0                         | 0                      | 63.425                      | 0                              | 2                        | 7                                        | Success                                             |
| [lanterna](https://github.com/mabe02/lanterna)                                               | `5982dbfd`     | 2.0%                  | 6207008/18483488 (66.41%)   | 0                         | 0                      | 365.703                     | 1                              | 5933                     | 32                                       | Success                                             |
| [java-apns](https://github.com/notnoop/java-apns)                                            | `180a190`      | --                    | --                          | --                        | --                     | --                          | --                             | --                       | --                                       | Unable to build original project due to test errors |
| [Mybatis-PageHelper](https://github.com/pagehelper/Mybatis-PageHelper)                       | `525394c`      | 23.9%                 | 1472015/4374855 (66.35%)    | 55                        | 0                      | 128.552                     | 3                              | 1948                     | 605                                      | Success                                             |
| [Algorithms](https://github.com/pedrovgs/Algorithms)                                         | `9ae21a5q`     | 5.5%                  | 89905/102350 (12.16%)       | 0                         | 0                      | 56.274                      | 0                              | 698                      | 0                                        | Success                                             |
| [fragmentargs](https://github.com/sockeqwe/fragmentargs)                                     | `5de3946`      | --                    | --                          | --                        | --                     | --                          | --                             | --                       | --                                       | This project is multi-module                        |
| [moshi](https://github.com/square/moshi)                                                     | `08bfeda`      | --                    | --                          | 0                         | --                     | --                          | --                             | --                       | --                                       | This project is multi-module                        |
| [tomighty](https://github.com/tomighty/tomighty)                                             | `cf05ca3`      | --                    | --                          | 0                         | --                     | --                          | --                             | --                       | --                                       | This project is multi-module                        |
| [zt-zip](https://github.com/zeroturnaround/zt-zip)                                           | `6933db7`      | 11.3%                 | 123307/137515 (10.33%)      | 0                         | 0                      | 60.147                      | 1                              | 11                       | 82                                       | Success                                             |
| [gwt-cal](X)                                                                                 | `--`           | --                    | --                          | --                        | --                     | --                          | --                             | --                       | --                                       | Unable to find the original project repository      |
| [Java-Chronicle](https://github.com/peter-lawrey/Java-Chronicle)                             | `64ba04e`      | --                    | --                          | --                        | --                     | --                          | --                             | --                       | --                                       | Success                                             |
| [maven-config-processor-plugin](https://github.com/lehphyro/maven-config-processor-plugin)   | `c92e588`      | 29.8%                 | 1596091/5900666 (72.95%)    | 0                         | 0                      | 612.322                     | 29                             | 2529                     | 422                                      | Success                                             |
| [jboss-logmanager](https://github.com/jboss-logging/jboss-logmanager.git)                    | `e574b1b`      | --                    | --                          | --                        | --                     | --                          | --                             | --                       | --                                       | Unable to build original project due to test errors |
| [AutoLoadCache](https://github.com/qiujiayu/AutoLoadCache)                                   | `06f67543`     | 20.2%                 | 5051583/15202103 (66.78%)   | 9                         | 0                      | 347.831                     | 2                              | 5714                     | 65                                       | Success                                             |
| [TProfiler](https://github.com/alibaba/TProfiler)                                            | `8344d1a`      | 10.2%                 | 17809/105214 (83.07%)       | 0                         | 0                      | 56.865                      | 1                              | 49                       | 13                                       | Success                                             |
| -------------------------------------------------------------------------------------------- | ------------   | --------------------- | --------------------------- | ------------------------- | ---------------------- | -----------------------     | ---------------------------    | ---------------          | -------------------------------          | --------------------------------------------------- |
| **TOTAL**                                                                                    | --             | --                    | --                          | 77                        | 0                      | 2400.086                    | 59                             | 20067                    | 4290                                     | --                                                  |
| **MEAN**                                                                                     | --             | 14.99%                | 34.65%                      | --                        | --                     | 150.00                      | --                             | --                       | --                                       | --                                                  |
| **MEDIAN**                                                                                   | --             | 11.4%                 | 17.05%                      | --                        | --                     | 79.32                       | --                             | --                       | --                                       | --                                                  |



# Unix commands used during the reproducibility of the benchmark

## Git checkout to the experiments' version:

```bash
git checkout `git rev-list -n 1 --before="2018-10-15 12:00" master`
```

## Get original and debloated JAR size in bytes:

```bash
gstat --format="%s" disklrucache-2.0.3-SNAPSHOT-jar-with-dependencies.jar
```

## Add `M2_HOME` and `JAVA_HOME` of specific JDK to `PATH` in macOS:

```bash
# Find all installed JDKs
/usr/libexec/java_home -V

export JAVA_HOME=/usr/bin/java
export PATH=$JAVA_HOME:$PATH
echo ${JAVA_HOME}

export M2_HOME=/usr/local/Cellar/maven/3.8.3/libexec/
export PATH=$M2_HOME:$PATH
echo ${M2_HOME}
```

## Set Java build version in POM file

```xml
<java.src.version>8</java.src.version>
<java.test.version>8</java.test.version>
```



















