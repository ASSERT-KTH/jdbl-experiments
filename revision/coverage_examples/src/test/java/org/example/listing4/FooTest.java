package org.example.listing4;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class FooTest {
  @Test
  public void test() {
    Foo foo = new Foo();
    assertEquals(42, foo.doMagic());
  }
}