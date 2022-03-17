package se.kth.classreader;

import java.io.File;
import java.io.FileInputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.LinkedList;
import org.apache.commons.io.FileUtils;
import se.kth.classreader.ClassReader.ClassAccess;

public class Main {

  public static void main(String[] args) {

    File resultsFile = new File("src/test/resources/class_types_all.csv");

    // Now analyze the class files in the decompressed JARs
    File dir = new File("src/test/resources/jars");
    Collection<File> files = FileUtils.listFiles(dir, new String[]{"class"}, true);
    for (File file : files) {

      try {
        ClassReader classReader = new ClassReader(new FileInputStream(file));
        Path path = Paths.get(file.getAbsolutePath());
        long fileSize = Files.size(path);
        LinkedList<ClassAccess> classAccesses = ClassAccess.get(classReader.struct.aflags);
        String line;
        if (classAccesses.contains(ClassAccess.INTERFACE) ||
            classAccesses.contains(ClassAccess.ENUM) ||
            classAccesses.contains(ClassAccess.ANNOTATION)
        ) {
          line = file.getName() + "," + "IGNORED" + "," + fileSize + "\n";
        } else {
          line = file.getName() + "," + "CONSIDERED" + "," + fileSize + "\n";
        }
        FileUtils.writeStringToFile(resultsFile, line, "UTF-8", true);
      } catch (Exception ignored) {
      }
    }
  }


  /**
   * Filter the original JARs from the results directory.
   * @throws Exception
   */
  public void getJars() throws Exception {
    File dir = new File("/Users/cesarsv/Documents/PAPERS/coverage_based_debloat/results");
    Collection<File> files = FileUtils.listFiles(dir, new String[]{"jar"}, true);
    int i = 0;
    for (File file : files) {
      if (file.getAbsolutePath().contains("/debloat/original.jar")) {
        FileUtils.copyFile(file, new File("src/test/resources/jars/" + i + ".jar"));
        i++;
      }
    }
  }

}
