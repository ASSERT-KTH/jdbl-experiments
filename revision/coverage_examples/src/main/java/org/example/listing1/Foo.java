package org.example.listing1;

/**
 * Hello world!
 */
public class Foo {

  public void m1(){
    m2();
  }

  public void m2(){
    throw new IllegalArgumentException();
  }

}



