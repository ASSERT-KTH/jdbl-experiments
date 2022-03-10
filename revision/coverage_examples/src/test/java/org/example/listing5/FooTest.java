package org.example.listing5;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class FooTest {
  @Test
  public void test() {
    long fileSize = 50000;
    Foo foo = new Foo();
    assertEquals("48 KB", foo.showFileSize(fileSize));
  }
}