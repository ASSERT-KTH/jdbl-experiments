# Execution script

## Usage

```bash
docker build -t jdbl .; docker run -v `pwd`/results:/results -it --rm jdbl -d <library> -c <client>
```

## Example
```bash
docker build -t jdbl .; docker run -v `pwd`/results:/results -it --rm jdbl -d https://github.com/apache/commons-cli.git -c https://github.com/1dir1/wordpress-java.git
```
