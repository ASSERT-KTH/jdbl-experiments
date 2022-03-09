package org.example.listing2;

public enum FooEnum {
  MAGIC("forty two");
  public final String label;
  private FooEnum(String label) {
    this.label = label;
  }
}
