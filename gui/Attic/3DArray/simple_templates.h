/*
  XRCL: The Extensible Robot Control Language
  (c) 2000, Douglas S. Blank
  University of Arkansas, Roboticists Research Group
  http://ai.uark.edu/xrcl/
  
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
  02111-1307, USA.

  As a special exception, you have permission to link this program
  with the Qt library and distribute executables, as long as you
  follow the requirements of the GNU GPL in regard to all of the
  software in the executable aside from Qt.
*/

/***************************************************************
Templates.h

  Templates implemented:
TCArray
TCList

Similar to ATL.  Not that I don't like the STL, I just don't
need anything big and fancy.
$Header$
$Log$
Revision 1.1  2002/03/26 02:57:23  dblank
Initial revision

Revision 1.1.1.1  2001/10/30 09:47:21  dblank
new version on emergent

Revision 1.1  2001/03/19 23:34:34  dblank
A C++ class that is graphics independent... just based on an array buffer. Fill isn't done yet.

Revision 1.3  2000/08/23 20:42:06  dblank
After competition

Revision 1.1.1.1  2000/07/30 15:25:52  robot
XRCL before the Austin competition

Revision 1.2  2000/07/12 03:14:33  dblank
Added GNU GPL Statement to all files

Revision 1.1  2000/03/05 01:35:34  dblank
Initial revision

Revision 1.1  2000/02/17 03:34:42  dblank
Initial revision

Revision 3.2  1999/06/24 05:00:05  dblank
Version 3.0

Revision 3.1  1999/06/24 04:40:19  dblank
Version 3.0

Revision 2.1  1999/06/10 21:28:04  jrg
fixed a problem with head and tail removal

Revision 2.0  1999/06/05 17:10:02  dblank
Version 2.0: threads, multi-behaviors, etc.

Revision 1.8  1999/06/05 02:48:23  dblank
Cleanup

Revision 1.7  1999/05/11 18:54:27  jrg
*** empty log message ***

Revision 1.6  1999/05/07 21:59:57  jrg
*** empty log message ***

Revision 1.5  1999/05/07 16:07:58  jrg
Added a destructor to release allocated data.

Revision 1.3  1999/05/06 13:13:11  jrg
Added Header and Log

****************************************************************/

#ifndef __SIMPLE_TEMPLATES_H__
#define __SIMPLE_TEMPLATES_H__

#include <stdlib.h>

typedef void * pPosition;
typedef pPosition POSITION;

class InitException { public: InitException(){} };
class UnderflowException { public: UnderflowException(){} };

/****************************************************************
Template TCArray
Array Template
****************************************************************/
template<class TYPE,class ARG_TYPE>
class TCArray {
private:
	TYPE * m_pData;
	long m_lSize;
	long m_lTop;
	long m_lGrowBy;
public:
/***************************************************************
****************************************************************/
	TCArray(void) :m_pData(NULL),m_lSize(0),m_lTop(0),m_lGrowBy(16)
	{
	}
	
	~TCArray(void)
	{
		if (m_pData != NULL ) {
			delete[] m_pData;
		}
	}
/***************************************************************
****************************************************************/
	void SetSize(long lSize,long lGrowBy = -1)
	{
		TYPE * pNewData;
		int i;
		
		if (lGrowBy  != -1)
			m_lGrowBy = lGrowBy;
			
		m_lTop = lSize;
		if (m_pData == NULL) {
			// create data
			m_pData = new TYPE[lSize];
			m_lSize = lSize;
		} else if (lSize == 0) {
			delete[] m_pData;
			m_pData = NULL;
			m_lSize = 0;
		} else if (lSize < m_lSize) {
			// shrink the data
			pNewData = new TYPE[lSize];
			for (i=0;i<lSize;i++)
				pNewData[i] = m_pData[i];
			m_lSize = lSize;
			delete[] m_pData;
			m_pData =  pNewData;
		} else {
			// let the data grow
			if (lSize < m_lSize+m_lGrowBy)
				lSize  += m_lGrowBy;
			
			pNewData = new TYPE[lSize];
			for (i=0;i<m_lSize;i++)
				pNewData[i] =  m_pData[i];
				
			m_lSize = lSize;
			delete[] m_pData;
			m_pData = pNewData;
		}
	}
	
/***************************************************************
****************************************************************/
	TYPE & operator[](long lPos)
	{
		if (lPos >= m_lTop) {
			m_lTop = lPos;
			/* TODO
			this could be a bit dangerous if lPos is 
			really big, need to come up with some good
			way of testing the size 
			*/
			if (lPos >= m_lSize)
				SetSize(lPos);
		}
		return m_pData[lPos];
	}

/***************************************************************
****************************************************************/
	TYPE operator[](long lPos) const
	{
		if (lPos >= m_lTop) {
			/* TODO:
			should really throw an out of bounds exception 
			*/
			if (m_pData != NULL)
				return m_pData[0];
			else {
				TYPE t;
				return t;
			}
		}
		return m_pData[lPos];
	}
	
/***************************************************************
****************************************************************/
	long Add(ARG_TYPE Value)
	{
		m_lTop++;
		if  (m_lTop >= m_lSize)
			SetSize(m_lTop);
		m_pData[m_lTop-1] = Value;
		return m_lTop;
	}

/***************************************************************
****************************************************************/
	long Add(ARG_TYPE Value) const
	{
		return m_lTop;
	}

/***************************************************************
****************************************************************/
	long GetTop(void) const
	{
		return m_lTop;
	}

/***************************************************************
****************************************************************/
	operator const TYPE * (void) const
	{
		return m_pData;
	}
};

/****************************************************************
Template TCList,
Linked list template class
****************************************************************/

template<class TYPE,class ARG_TYPE>
class TCList {
private:
	typedef struct sListEntry {
		struct sListEntry *pNext, *pPrev;
		TYPE data;
	} tListEntry;
	
	tListEntry * m_pHead,*m_pTail;
	long m_lSize;
	long m_lGrowBy;
	long m_lCount;

public:
/****************************************************************
****************************************************************/
	TCList(void) { m_pHead = m_pTail = NULL; m_lCount = 0; }
/***************************************************************
****************************************************************/
	~TCList(void) { RemoveAll(); }
/***************************************************************
****************************************************************/
	POSITION AddHead(ARG_TYPE data)
	{
		tListEntry * pNewEntry;
		pNewEntry = new tListEntry;
		if (!pNewEntry) // make sure we have it
			return NULL;
		pNewEntry->pNext = pNewEntry->pPrev = NULL;
		pNewEntry->data = data;
		if (m_pHead) // if there's a head replace it
		{
			pNewEntry->pNext = m_pHead;
			m_pHead->pPrev = pNewEntry;
		}
		else
			m_pTail = pNewEntry;
		m_pHead = pNewEntry;
		m_lCount++;
		return static_cast<void *>(pNewEntry);
	}
/***************************************************************
****************************************************************/
	POSITION AddTail(ARG_TYPE data)
	{
		tListEntry * pNewEntry;
		pNewEntry = new tListEntry;
		if (!pNewEntry) // make sure we have it
			return NULL;
		pNewEntry->pNext = pNewEntry->pPrev = NULL;
		pNewEntry->data = data;
		if (m_pTail) // if there's a tail replace it
		{
			pNewEntry->pPrev = m_pTail;
			m_pTail->pNext = pNewEntry;
		}
		else
			m_pHead = pNewEntry;
		m_pTail = pNewEntry;
		m_lCount++;
		
		return static_cast<void *>(pNewEntry);
	}
/***************************************************************
****************************************************************/
	TYPE RemoveHead(void)
	{
		tListEntry * pToRemove;
		TYPE ReturnValue;
		// make sure there is a head, m_lCount should never go
		// below zero
		if (!m_pHead || m_lCount <= 0) {
			m_pTail = m_pHead = NULL;
			return ReturnValue; 
		}
		pToRemove = m_pHead;
		m_pHead = m_pHead->pNext;
		if (m_pHead)
			m_pHead->pPrev = NULL;
		ReturnValue = pToRemove->data;
		delete pToRemove;
		m_lCount--;
	
		if (!m_pHead || m_lCount <= 0) {
			m_pTail = m_pHead = NULL;
		}

		return ReturnValue;
	}
/***************************************************************
****************************************************************/
	TYPE RemoveTail(void)
	{
		tListEntry * pToRemove;
		TYPE ReturnValue;
		// make sure there is a head, m_lCount should never go
		// below zero
		if (!m_pTail || m_lCount <= 0) {
			m_pTail = m_pHead = NULL;
			return ReturnValue; 
		}
		pToRemove = m_pTail;
		m_pTail = m_pTail->pPrev;
		if (m_pTail)
			m_pTail->pNext = NULL;
		ReturnValue = pToRemove->data;
		delete pToRemove;
		m_lCount--;
		if (!m_pTail || m_lCount <= 0) {
			m_pTail = m_pHead = NULL;
		}
		return ReturnValue;
	}

/***************************************************************
****************************************************************/
	void RemoveAll(void)
	{
		while (!IsEmpty())
			RemoveHead();
	}
/***************************************************************
****************************************************************/
	TYPE GetAtHead(void)
	{
		TYPE r;
		if (m_pHead)
			return m_pHead->data;
		else
			return r;
	}
/***************************************************************
****************************************************************/
	TYPE GetAtTail(void)
	{
		TYPE r;
		if (m_pTail)
			return m_pTail->data;
		else
			return r;
	}
/***************************************************************
****************************************************************/
	POSITION GetHeadPosition(void)
	{
		return static_cast<pPosition>(m_pHead);
	}
/***************************************************************
****************************************************************/
	POSITION GetTailPosition(void)
	{
		return (pPosition)m_pTail;
	}
/***************************************************************
****************************************************************/
	TYPE GetNext(pPosition & pos)
	{
		if (!pos)
			pos = m_pHead;
		TYPE & data = ((tListEntry *)pos)->data;
		pos = static_cast<pPosition>(((tListEntry *)pos)->pNext);
		return data;
	}
/***************************************************************
****************************************************************/
	TYPE GetPrev(pPosition & pos)
	{
		TYPE data;
		if (!pos)
			pos = m_pTail;
		data = ((tListEntry *)pos)->data;
		pos = (pPosition)((tListEntry *)pos)->pPrev;
		return data;
	}
/***************************************************************
****************************************************************/
	TYPE GetAt(pPosition pos)
	{
		TYPE data;
		if (!pos)
			pos = m_pHead;
		data = ((tListEntry *)pos)->data;
		return data;
	}

/***************************************************************

***************************************************************/
	pPosition InsertBefore(pPosition pos,ARG_TYPE data)
	{
		tListEntry * pNewEntry;

		pNewEntry = new tListEntry;
		if (!pNewEntry) // make sure we have it
			return NULL;

		pNewEntry->pNext = pNewEntry->pPrev = NULL;
		pNewEntry->data = data;

		// take special care if inserting before the head of the list
		if (pos == m_pHead || pos == NULL) {
			pNewEntry->pNext = m_pHead;
			m_pHead->pPrev = pNewEntry;
			m_pHead = pNewEntry;
		} else {
			pNewEntry->pPrev = ((tListEntry *)pos)->pPrev;
			pNewEntry->pNext = ((tListEntry *)pos);
			pNewEntry->pNext->pPrev = pNewEntry;
			if (pNewEntry->pPrev)
				pNewEntry->pPrev->pNext = pNewEntry;
		}
		m_lCount++;

		return pNewEntry;
	}

/***************************************************************

***************************************************************/
	pPosition InsertAfter(pPosition pos,ARG_TYPE data)
	{
		tListEntry * pNewEntry;

		pNewEntry = new tListEntry;
		if (!pNewEntry) // make sure we have it
			return NULL;

		pNewEntry->pNext = pNewEntry->pPrev = NULL;
		pNewEntry->data = data;

		// take special care if inserting before the head of the list
		if (pos == m_pTail || pos == NULL) {
			pNewEntry->pPrev = m_pTail;
			m_pHead->pNext = pNewEntry;
			m_pTail = pNewEntry;
		} else {
			pNewEntry->pNext = ((tListEntry *)pos)->pNext;
			pNewEntry->pPrev = ((tListEntry *)pos);
			pNewEntry->pPrev->pNext = pNewEntry;
			if (pNewEntry->pNext)
				pNewEntry->pNext->pPrev = pNewEntry;
		}
		m_lCount++;

		return pNewEntry;
	}

/***************************************************************


// to delete a list of allocated data
pPosition = NULL;
do {
	delete List.RemoveAt(pos);
} while(pos);

****************************************************************/
	TYPE RemoveAt(pPosition & pos,bool bMoveUp = true)
	{
		TYPE data;
		tListEntry * pEntry;

		if (!pos)
			pos = (pPosition)m_pHead;

		pEntry = (tListEntry *)pos;

		if (pEntry == m_pHead) {
			data = GetNext(pos);
			RemoveHead();
			if ( m_lCount <= 0 )
				m_pTail = m_pHead = NULL;
			return data;
		} 
		
		if (pEntry == m_pTail) {
			pos = (pPosition)m_pTail;
			data = GetPrev(pos);
			RemoveTail();
			if ( m_lCount <= 0 )
				m_pTail = m_pHead = NULL;
			return data;
		}


		if (bMoveUp)
			data = GetNext(pos);
		else
			data = GetPrev(pos);
			
		// these should be valid entries
		pEntry->pNext->pPrev = pEntry->pPrev;
		pEntry->pPrev->pNext = pEntry->pNext;
		m_lCount--;
		if ( m_lCount <= 0 )
			m_pTail = m_pHead = NULL;
		return data;
	}	
/***************************************************************
****************************************************************/
	long GetCount(void){return m_lCount;}
	bool IsEmpty(){ return (m_lCount == 0); }
};


/***************************************************************
Queue Template
****************************************************************/
template <class TYPE,class ARG_TYPE>
class TCQueue {
private:
	TCArray<TYPE,ARG_TYPE> * m_paData;
	long m_lSize;
	long m_lTail;
	long m_lHead;
public:
	
/***************************************************************
****************************************************************/
	TCQueue(const TCQueue & rhs)
	{
		long index,length;
		
		m_lSize = rhs.m_lSize;
		m_paData = new TCArray<TYPE,ARG_TYPE>;
		m_paData->SetSize(m_lSize);	
		
		length = rhs.GetQueueLength();
		
		for(index=0;index<length;index++)
			(*m_paData)[index] = rhs[index];
		m_lHead = length;
		m_lTail = 0;
		
	}
	
/***************************************************************
****************************************************************/
	TCQueue( void ) : 
		m_paData(NULL),m_lSize(0),m_lTail(0),m_lHead(0)
	{
	}
	
/***************************************************************
****************************************************************/
	TCQueue( long lSize ) :
		m_paData(NULL),m_lSize(lSize+1),m_lTail(0),m_lHead(0)
	{
		m_paData = new TCArray<TYPE,ARG_TYPE>;
		m_paData->SetSize(m_lSize);
	}


	~TCQueue( void ) 
	{
		if (m_paData)
			delete m_paData;
	}
/***************************************************************
****************************************************************/
	long GetQueueLength( void )
	{
		return ((m_lHead - m_lTail)+m_lSize) % m_lSize;
	}

/***************************************************************
****************************************************************/
	void SetSize( long lSize )
	{
		long index,length;
		TCArray<TYPE,ARG_TYPE> * pNewArray;
		
		if (m_paData) {
			// get a new array
			pNewArray = new TCArray<TYPE,ARG_TYPE>;
			pNewArray->SetSize(lSize+1);
			// get the right size
			length = GetQueueLength();
			if (length >= lSize)
				length = lSize;

			for (index=0;index<length;index++) 
				(*pNewArray)[index] = GetAt(index);

			delete m_paData;

			m_paData = pNewArray;
			m_lHead = length;
			m_lTail = 0;
			m_lSize = lSize+1;
			
		} else {
			m_paData = new TCArray<TYPE,ARG_TYPE>;
			m_paData->SetSize(lSize+1);
			m_lHead = 0;
			m_lTail = 0;
			m_lSize = lSize+1;
		}
	}

/***************************************************************
****************************************************************/
	TYPE GetAt(long lIndex)
	{
		if (!m_paData) 
			throw InitException();
		return (*m_paData)[(lIndex+m_lTail)%m_lSize];
	}

/***************************************************************
****************************************************************/
	TYPE operator[](long lIndex)
	{
		return GetAt(lIndex);
	}
	
/***************************************************************
****************************************************************/
	TYPE Push(ARG_TYPE value)
	{
		if (!m_paData) 
			throw InitException();
		m_lHead = (m_lHead+1) % m_lSize;
		if (m_lHead == m_lTail)
			m_lTail = (m_lTail+1) % m_lSize;
		(*m_paData)[m_lHead] = value;
		return value;
	}

/***************************************************************
****************************************************************/
	TYPE Pop( void )
	{
	
		if (!m_paData) 
			throw InitException();
		if (m_lHead == m_lTail)
			throw UnderflowException();

		ARG_TYPE ReturnValue = (*m_paData)[m_lTail];		
		m_lTail = (m_lTail+1) % m_lSize;
		return ReturnValue;
		
	}
};

#endif
