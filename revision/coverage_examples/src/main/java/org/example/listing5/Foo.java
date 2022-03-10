package org.example.listing5;

import org.apache.commons.io.FileUtils;

/**
 * Get Readable File Size from Number of Bytes in Java using Apache Commons IO
 */
public class Foo {
  public String showFileSize(long fileSize) {
    return FileUtils.byteCountToDisplaySize(fileSize);
  }
}
