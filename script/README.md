# Execution script

## Usage

```bash
docker build -t jdbl .; docker run -v `pwd`/results:/results -it --rm jdbl -d <library> -c <client>
```

The output of the script is put in the folder results

## Example
```bash
docker build -t jdbl .; docker run -v `pwd`/results:/results -it --rm jdbl -d https://github.com/apache/commons-cli.git -c https://github.com/1dir1/wordpress-java.git
```

## Results

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