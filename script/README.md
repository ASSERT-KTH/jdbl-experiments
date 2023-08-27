# Execution script

## Usage

```bash
export JDBL_COMMIT=c57396a5739e6ac3b0fa434342eb57b6f945914b # commit of JDBL that you want to use
docker build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg LIB_VER=$JDBL_COMMIT -t tdurieux/jdbl .; docker run -v `pwd`/results:/home/jdbl/results/ -it --rm tdurieux/jdbl -d <library> -c <client>
```

The output of the script is put in the folder results

## Example
```bash
export JDBL_COMMIT=c57396a5739e6ac3b0fa434342eb57b6f945914b # commit of JDBL that you want to use
docker build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg LIB_VER=$JDBL_COMMIT -t jdbl .; docker run -v `pwd`/results:/results -it --rm jdbl -d https://github.com/apache/commons-cli.git -c https://github.com/1dir1/wordpress-java.git
```

## Results

### Analysing the results

`./generateStat.py --output <results_path>` contains the script that extracts all the data used to write our paper.
The script generates 2 files `raw_results.csv` and `raw_results.json`. 
They contain mostly the same information but presented in a different format.

`./rq*.py` contains the scripts that generates the main tables and metric of our paper, the output is in Latex which is directly copy/past in our paper.


### Raw data

```
results
    <library>/
        <library_version>/
            original/
                original.jar
                test-results/
            debloat/
                debloat.jar
                test-results/
                coverage.exec
            clients/
                <client>
                    original/
                        test-results/
                    debloat/
                        test-results/
```