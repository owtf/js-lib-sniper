// This implements the typedefs for the OpenGL data types.
//
// Copyright (c) 2014 Riverbank Computing Limited <info@riverbankcomputing.com>
// 
// This file is part of PyQt.
// 
// This file may be used under the terms of the GNU General Public
// License versions 2.0 or 3.0 as published by the Free Software
// Foundation and appearing in the files LICENSE.GPL2 and LICENSE.GPL3
// included in the packaging of this file.  Alternatively you may (at
// your option) use any later version of the GNU General Public
// License if such license has been publicly approved by Riverbank
// Computing Limited (or its successors, if any) and the KDE Free Qt
// Foundation. In addition, as a special exception, Riverbank gives you
// certain additional rights. These rights are described in the Riverbank
// GPL Exception version 1.1, which can be found in the file
// GPL_EXCEPTION.txt in this package.
// 
// If you are unsure which license is appropriate for your use, please
// contact the sales department at sales@riverbankcomputing.com.
// 
// This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
// WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


typedef char GLchar;
typedef qint8 GLbyte;
typedef quint8 GLubyte;
typedef quint8 GLboolean;
typedef qint16 GLshort;
typedef quint16 GLushort;
typedef qint32 GLint;
typedef qint32 GLsizei;
typedef quint32 GLuint;
typedef quint32 GLenum;
typedef quint32 GLbitfield;
%If (PyQt_NoOpenGLES)
typedef quint64 GLuint64;       // This is in OpenGL ES v3.
typedef double GLdouble;
%End
typedef float GLfloat;
typedef float GLclampf;
typedef long GLintptr;
typedef long GLsizeiptr;
