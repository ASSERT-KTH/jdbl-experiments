package org.example.listing1;

import static org.junit.Assert.assertTrue;

import org.example.listing1.Foo;
import org.junit.Test;

/**
 * Unit test for simple App.
 */
public class FooTest {

  /**
   * Rigorous Test :-)
   */
  @Test(expected = IllegalArgumentException.class)
  public void test() {
   Foo foo = new Foo();
   foo.m1();
  }

}
