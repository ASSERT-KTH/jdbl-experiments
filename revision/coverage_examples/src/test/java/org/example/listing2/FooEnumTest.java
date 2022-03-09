package org.example.listing2;

import org.junit.Test;
import static org.junit.Assert.*;

public class FooEnumTest {

  @Test
  public void test() {
    assertEquals("forty two", FooEnum.valueOf("MAGIC").label);
  }
}