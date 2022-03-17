package se.kth.classreader;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.io.File;
import java.io.FileInputStream;
import java.util.LinkedList;
import org.junit.Test;
import se.kth.classreader.ClassReader.ClassAccess;

public class ClassReaderTest {

  @Test
  public void testClassIsInterface() throws Exception {
    File classFile = new File("src/test/resources/Adaptable.class");
    ClassReader classReader = new ClassReader(new FileInputStream(classFile));
    LinkedList<ClassAccess> classAccesses = ClassAccess.get(classReader.struct.aflags);
    assertTrue(classAccesses.contains(ClassAccess.INTERFACE));
  }

  @Test
  public void testClassIsNotInterface() throws Exception {
    File classFile = new File("src/test/resources/PathSet.class");
    ClassReader classReader = new ClassReader(new FileInputStream(classFile));
    LinkedList<ClassAccess> classAccesses = ClassAccess.get(classReader.struct.aflags);
    assertFalse(classAccesses.contains(ClassAccess.INTERFACE));
  }

  @Test
  public void testClassIsAnnotation() throws Exception {
    File classFile = new File("src/test/resources/ConsumerType.class");
    ClassReader classReader = new ClassReader(new FileInputStream(classFile));
    LinkedList<ClassAccess> classAccesses = ClassAccess.get(classReader.struct.aflags);
    assertTrue(classAccesses.contains(ClassAccess.ANNOTATION));
  }

  @Test
  public void testClassIsNotAnnotation() throws Exception {
    File classFile = new File("src/test/resources/Adaptable.class");
    ClassReader classReader = new ClassReader(new FileInputStream(classFile));
    LinkedList<ClassAccess> classAccesses = ClassAccess.get(classReader.struct.aflags);
    assertFalse(classAccesses.contains(ClassAccess.ANNOTATION));
  }

  @Test
  public void testClassIsException() throws Exception {
    File classFile = new File("src/test/resources/Adaptable.class");
    ClassReader classReader = new ClassReader(new FileInputStream(classFile));
    LinkedList<ClassAccess> classAccesses = ClassAccess.get(classReader.struct.aflags);
    assertFalse(classAccesses.contains(ClassAccess.ANNOTATION));
  }

}