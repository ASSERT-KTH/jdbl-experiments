package se.kth.classreader;

import java.io.ByteArrayInputStream;
import java.io.DataInputStream;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.lang.reflect.Array;
import java.util.LinkedList;

public class ClassReader {

  public enum ClassAccess {

    PUBLIC(0x0001),
    FINAL(0x0010), SUPER(0x0020),
    INTERFACE(0x0200), ABSTRACT(0x0400),
    SYNTHETIC(0x1000), ANNOTATION(0x2000), ENUM(0x4000),
    UNDEFINED(0x0000);
    int flag;

    private ClassAccess(int flag) {
      this.flag = flag;
    }

    public static LinkedList<ClassAccess> get(int flag) {
      LinkedList<ClassAccess> flags = new LinkedList<>();
      if ((flag & 0x0001) > 0) {
        flags.add(PUBLIC); // May be accessed from outside the package.
      }
      if ((flag & 0x0010) > 0) {
        flags.add(FINAL); // Cannot be subclassed. mutex with INTERFACE and ABSTRACT
      }
      if ((flag & 0x0020) > 0) {
        flags.add(SUPER); // For backward compatibility, special invocation instruction
      }
      if ((flag & 0x0200) > 0) {
        flags.add(INTERFACE); // Interface - Must also have ABSTRACT set and mutex with FINAL, SUPER, ENUM
      }
      if ((flag & 0x0400) > 0) {
        flags.add(ABSTRACT); // Cannot be instantiated
      }
      if ((flag & 0x1000) > 0) {
        flags.add(SYNTHETIC); // Compiler generated, will not be included in the src
      }
      if ((flag & 0x2000) > 0) {
        flags.add(ANNOTATION); // @Annotation must also have INTERFACE set
      }
      if ((flag & 0x4000) > 0) {
        flags.add(ENUM); // ENUM type
      }

      return flags;
    }
  }

  public enum FieldAccess {

    PUBLIC(0x0001),
    PRIVATE(0x0002), PROTECTED(0x0004),
    STATIC(0x0008), FINAL(0x0010),
    VOLATILE(0x0040), TRANSIENT(0x0080), SYNTHETIC(0x1000),
    ENUM(0x4000);
    int flag;

    private FieldAccess(int flag) {
      this.flag = flag;
    }

    public static LinkedList<FieldAccess> get(int flag) {
      LinkedList<FieldAccess> flags = new LinkedList<FieldAccess>();
      if ((flag & 0x0001) > 0) {
        flags.add(PUBLIC); // May be accessed from outside the class
      }
      if ((flag & 0x0002) > 0) {
        flags.add(PRIVATE); // Usable only within the defining class.
      }
      if ((flag & 0x0004) > 0) {
        flags.add(PROTECTED); // May only be accessed from class and subclasses
      }
      if ((flag & 0x0008) > 0) {
        flags.add(STATIC); // Static
      }
      if ((flag & 0x0010) > 0) {
        flags.add(FINAL); // Cannot be changed during instantiation
      }
      if ((flag & 0x0040) > 0) {
        flags.add(VOLATILE); // Cannot be cached
      }
      if ((flag & 0x0080) > 0) {
        flags.add(TRANSIENT); // Not written/read by persistent object managers
      }
      if ((flag & 0x1000) > 0) {
        flags.add(SYNTHETIC); // Compiler generated, will not be included in the src
      }
      if ((flag & 0x4000) > 0) {
        flags.add(ENUM); // ENUM type
      }
      return flags;
    }
  }

  public enum MethodAccess {

    PUBLIC(0x0001),
    PRIVATE(0x0002), PROTECTED(0x0004),
    STATIC(0x0008), FINAL(0x0010), SYNCHRONIZED(0x0020),
    BRIDGE(0x0040), VARARGS(0x0080), NATIVE(0x0100), ABSTRACT(0x0400), STRICT(0x0800), SYNTHETIC(0x1000);
    int flag;

    private MethodAccess(int flag) {
      this.flag = flag;
    }

    public static LinkedList<MethodAccess> get(int flag) {
      LinkedList<MethodAccess> flags = new LinkedList<MethodAccess>();
      if ((flag & 0x0001) > 0) {
        flags.add(PUBLIC); // May be accessed from outside the class
      }
      if ((flag & 0x0002) > 0) {
        flags.add(PRIVATE); // Usable only within the defining class.
      }
      if ((flag & 0x0004) > 0) {
        flags.add(PROTECTED); // May only be accessed from class and subclasses
      }
      if ((flag & 0x0008) > 0) {
        flags.add(STATIC); // Static
      }
      if ((flag & 0x0010) > 0) {
        flags.add(FINAL); // Cannot be changed during instantiation
      }
      if ((flag & 0x0020) > 0) {
        flags.add(SYNCHRONIZED); // Threadsafe
      }
      if ((flag & 0x0040) > 0) {
        flags.add(BRIDGE); // Compiler generated bridge method
      }
      if ((flag & 0x0080) > 0) {
        flags.add(VARARGS); // Variable number of args : variadic
      }
      if ((flag & 0x0100) > 0) {
        flags.add(NATIVE); // Not a java method
      }
      if ((flag & 0x0400) > 0) {
        flags.add(ABSTRACT); // No implementation is provided
      }
      if ((flag & 0x0800) > 0) {
        flags.add(STRICT); // Strict floating point manipulation
      }
      if ((flag & 0x1000) > 0) {
        flags.add(SYNTHETIC); // Compiler generated, will not be included in the src
      }
      return flags;
    }


  }

  class ClassStruct {

    int magic = 0xCAFEBABE;
    short minor_version = 0;
    short major_version = 0;
    short cpool_count = 0;
    Object[] cpool;
    short aflags;
    short self = 0;
    short parent = 0;
    short interfaces_count = 0;
    short[] interfaces;
    short fields_count = 0;
    FieldStruct[] fields;
    short methods_count = 0;
    MethodStruct[] methods;
    short attributes_count = 0;
    AttributeStruct[] attributes;
  }

  class AttributeStruct {

    class LineNumberTable {

      short length;
      short[][] line_number_table;

    }

    class LocalVariableTable {

      short length;

      short[][] local_variable_table;

      public String[][] localStack(ClassReader reader) throws Exception {
        String[][] stack = new String[length][2];
        int i = 0;
        for (short[] local : local_variable_table) {
          stack[i++] = new String[]{(String) (reader.resolve(local[2])), (String) (reader.resolve(local[3]))};
        }
        return stack;
      }

    }

    class Code {

      short max_stack;
      short max_locals;
      int code_length;
      byte[] code;
      short exception_length;
      short[][] exceptions;
      short attributes_count;
      AttributeStruct[] attributes;

      public void printCode() {
        int cursor = 0;
        for (byte c : code) {
          int k = (int) ((char) c % 256);
          cursor++;
          System.out.print(
              ((cursor - 1) % 20 == 0 ? (cursor / 20) + " | " : "") + (k <= 0x0F ? "0" : "") + Integer.toHexString(k).toUpperCase() + (cursor % 10 == 0 ? (cursor % 20 != 0 ? "    " : "\n") : " "));
        }
        System.out.println("\n");
      }
    }

    short name;
    int alength;
    byte[] info;

    Object o;

    public void parseInfo(ClassReader reader) throws Exception {
      String name_ = (String) reader.resolve(this.name);
      if (name_.equals("ConstantValue")) {
        o = reader.resolve((short) ((info[0] << 8) + info[1]));
      } else if (name_.equals("Signature")) {
        o = reader.resolve((short) ((info[0] << 8) + info[1]));
      } else if (name_.equals("LineNumberTable")) {
        DataInputStream bytes = new DataInputStream(new ByteArrayInputStream(info));
        LineNumberTable table = new LineNumberTable();
        table.length = bytes.readShort();
        table.line_number_table = new short[table.length][2];
        for (int i = 0; i < table.length; i++) {
          table.line_number_table[i] = new short[]{bytes.readShort(), bytes.readShort()};
        }
        o = table;
      } else if (name_.equals("LocalVariableTable")) {
        DataInputStream bytes = new DataInputStream(new ByteArrayInputStream(info));
        LocalVariableTable table = new LocalVariableTable();
        table.length = bytes.readShort();
        table.local_variable_table = new short[table.length][5];
        for (int i = 0; i < table.length; i++) {
          table.local_variable_table[i] = new short[]{bytes.readShort(), bytes.readShort(), (short) (bytes.readShort() - (short) 1), (short) (bytes.readShort() - (short) 1), bytes.readShort()};
        }
        o = table;
      } else if (name_.equals("Code")) {
        DataInputStream bytes = new DataInputStream(new ByteArrayInputStream(info));
        Code code = new Code();
        code.max_stack = bytes.readShort();
        code.max_locals = bytes.readShort();
        code.code_length = bytes.readInt();
        code.code = new byte[code.code_length];
        bytes.read(code.code);
        code.exception_length = bytes.readShort();
        code.exceptions = new short[code.exception_length][4];
        for (int i = 0; i < code.exception_length; i++) {
          code.exceptions[i] = new short[]{bytes.readShort(), bytes.readShort(), bytes.readShort(), bytes.readShort()};
        }
        code.attributes_count = bytes.readShort();
        code.attributes = new AttributeStruct[code.attributes_count];
        for (int i = 0; i < code.attributes_count; i++) {
          AttributeStruct a = new AttributeStruct();
          a.name = (short) (bytes.readShort() - (short) 1);
          a.alength = bytes.readInt();
          a.info = new byte[a.alength];
          bytes.read(a.info);
          a.parseInfo(reader);
          code.attributes[i] = a;
        }
        o = code;
      } else {
        //print("Unknown Attribute " + name_);
        o = info;
      }
    }

  }

  class FieldStruct {

    short aflags;
    short name;
    short descriptor;
    short attributes_count;
    AttributeStruct[] attributes;

  }

  class MethodStruct {

    short aflags;
    short name;
    short descriptor;
    short attributes_count;
    AttributeStruct[] attributes;

  }

  DataInputStream source;
  ClassStruct struct = new ClassStruct();

  public static String parseDescriptor(String descriptor) {
    if (descriptor.startsWith("(")) {
      int starts = descriptor.indexOf(")", 0);
      String postfix = descriptor.substring(starts + 1);
      String prefix = descriptor.substring(1, starts);
      return parseDescriptor(postfix) + " %s(" + (prefix.isEmpty() ? "" : (parseDescriptor(prefix) + " %s")) + ")";
    }
    String array = "";
    while (descriptor.startsWith("[")) {
      array += "[]";
      descriptor = descriptor.substring(1);
    }
    if (descriptor.isEmpty()) {
      return "";
    }
    char tag = descriptor.charAt(0);
    descriptor = descriptor.substring(1);
    String obj = "";
    switch (tag) {
      case 'B':
        obj = "byte";
        break;
      case 'C':
        obj = "char";
        break;
      case 'D':
        obj = "double";
        break;
      case 'F':
        obj = "float";
        break;
      case 'I':
        obj = "int";
        break;
      case 'J':
        obj = "long";
        break;
      case 'S':
        obj = "short";
        break;
      case 'Z':
        obj = "boolean";
        break;
      case 'V':
        obj = "void";
        break;
      case 'L':
        int next = descriptor.indexOf(";", 0);
        obj = ClassReader.parseQualifiedName(descriptor.substring(0, next));
        descriptor = descriptor.substring(next + 1);
        break;
    }
    return obj + array + (descriptor.isEmpty() ? "" : " %s, " + parseDescriptor(descriptor));
  }

  public Object resolve(short index) throws Exception {
    if (index >= 0 && index < struct.cpool_count) {
      Object o = struct.cpool[index];
      if (o.getClass().isArray()) {
        short tag = (short) Array.get(o, (short) 0);
        switch (tag) {
          // 9,10,11
          case 0x09:
          case 0x0A:
          case 0x0B:
            Object class_ = resolve((short) Array.get(o, 1));
            Object descriptor = resolve((short) Array.get(o, 2));
            return new Object[]{class_, descriptor};
          case 0x07:
            return parseQualifiedName((String) resolve((short) Array.get(o, 1)));
          case 0x08:
            return resolve((short) Array.get(o, 1));
          case 0x0C:
            Object name = parseQualifiedName((String) resolve((short) Array.get(o, 1)));
            Object type = parseDescriptor((String) resolve((short) Array.get(o, 2)));
            return new String[]{(String) name, (String) type};
          default:
            throw new Exception("Fell through the cpool during symbol lookup. " + tag);
        }
      } else {
        return struct.cpool[index];
      }
    }
    return null;
  }

  public static void print(Object o, String end) {
    if (o.getClass().isArray()) {
      System.out.print("{");
      for (int i = 0; i < Array.getLength(o) - 1; i++) {
        print(Array.get(o, i), ", ");
      }
      print(Array.get(o, Array.getLength(o) - 1), "");
      System.out.print("}");
    } else if (o instanceof String) {
      System.out.print("\"" + o + "\"");
    } else {
      System.out.print(o);
    }
    System.out.print(end);
  }

  public static void print(Object o) {
    print(o, "\n");
  }

  public static void print(Object... objs) {
    if (objs.length < 5) {
      for (Object o : objs) {
        print(o, "\t");
      }

    } else {
      print(objs, "");

    }
    System.out.println();
  }

  public ClassReader(FileInputStream stream) throws IOException, Exception {
    source = new DataInputStream(stream);

    // Validate the magic number
    assert source.readInt() == 0xCAFEBABE;

    // Versioning
    struct.minor_version = source.readShort();
    struct.major_version = source.readShort();

    if (struct.major_version < 49) {
      throw new Exception("Java SDK not supported, only se > 5.0");
    }

    // Constant pool
    struct.cpool_count = (short) (source.readShort() - ((short) 1));
    struct.cpool = new Object[struct.cpool_count];
    for (int i = 0; i < struct.cpool_count; i++) {
      byte tag = source.readByte();
      switch (tag) {
        case 0x01:
          struct.cpool[i] = source.readUTF();
          break;
        case 0x03:
          struct.cpool[i] = source.readInt();
          break;
        case 0x04:
          struct.cpool[i] = source.readFloat();
          break;
        case 0x05:
          struct.cpool[i] = source.readLong();
          struct.cpool[++i] = struct.cpool[i - 1];
          break;
        case 0x06:
          struct.cpool[i] = source.readDouble();
          struct.cpool[++i] = struct.cpool[i - 1];
          break;
        case 0x08:
        case 0x07:
          struct.cpool[i] = new short[]{tag, (short) (source.readShort() - (short) 1)};
          break;
        case 0x09:
        case 0x0A:
        case 0x0B:
        case 0x0C:
          struct.cpool[i] = new short[]{tag,
              (short) (source.readShort() - (short) 1),
              (short) (source.readShort() - (short) 1)};
          break;
        default:
          //throw new Exception("Fell through cpool switch with tag " + tag + " at " + i);
          continue;
      }
    }

    // Access Flags / Bitmasks
    struct.aflags = source.readShort();

    // This/Super
    struct.self = (short) (source.readShort() - 1);
    struct.parent = (short) (source.readShort() - 1);
    if (struct.parent < 0) {
      struct.parent = 0; // TODO: resolve to java/lang/Object
    }
    // Interfaces
    struct.interfaces_count = source.readShort();
    struct.interfaces = new short[struct.interfaces_count];
    for (int i = 0; i < struct.interfaces_count; i++) {
      struct.interfaces[i] = (short) (source.readShort() - (short) 1);
    }

    // Fields
    struct.fields_count = source.readShort();
    struct.fields = new FieldStruct[struct.fields_count];
    for (int i = 0; i < struct.fields_count; i++) {
      FieldStruct field = new FieldStruct();
      field.aflags = source.readShort();
      field.name = (short) (source.readShort() - (short) 1);
      field.descriptor = (short) (source.readShort() - (short) 1);
      field.attributes_count = source.readShort();
      field.attributes = new AttributeStruct[field.attributes_count];
      for (int j = 0; j < field.attributes_count; j++) {
        AttributeStruct attr = new AttributeStruct();
        attr.name = (short) (source.readShort() - (short) 1);
        attr.alength = source.readInt();
        attr.info = new byte[attr.alength];
        for (int b = 0; b < attr.alength; b++) {
          attr.info[b] = source.readByte();
        }
        attr.parseInfo(this);
        field.attributes[j] = attr;
      }
      struct.fields[i] = field;
    }

    // Methods
    struct.methods_count = source.readShort();
    struct.methods = new MethodStruct[struct.methods_count];
    for (int i = 0; i < struct.methods_count; i++) {
      MethodStruct method = new MethodStruct();
      method.aflags = source.readShort();
      method.name = (short) (source.readShort() - (short) 1);
      method.descriptor = (short) (source.readShort() - (short) 1);
      method.attributes_count = source.readShort();
      method.attributes = new AttributeStruct[method.attributes_count];
      for (int j = 0; j < method.attributes_count; j++) {
        AttributeStruct attr = new AttributeStruct();
        attr.name = (short) (source.readShort() - (short) 1);
        attr.alength = source.readInt();
        attr.info = new byte[attr.alength];
        for (int b = 0; b < attr.alength; b++) {
          attr.info[b] = source.readByte();
        }
        attr.parseInfo(this);
        method.attributes[j] = attr;
      }
      struct.methods[i] = method;
    }

    // Attributes
    struct.attributes_count = source.readShort();
    struct.attributes = new AttributeStruct[struct.attributes_count];
    for (int i = 0; i < struct.attributes_count; i++) {
      AttributeStruct attr = new AttributeStruct();
      attr.name = (short) (source.readShort() - (short) 1);
      attr.alength = source.readInt();
      attr.info = new byte[attr.alength];
      for (int b = 0; b < attr.alength; b++) {
        attr.info[b] = source.readByte();
      }
      attr.parseInfo(this);
      struct.attributes[i] = attr;
    }
  }

  public ClassReader(String filename) throws FileNotFoundException, IOException, Exception {
    this(new FileInputStream(filename));
  }

  public static String parseQualifiedName(String name) {
    return name.replace('/', '.');
  }

}