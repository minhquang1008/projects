/*YTD*/

/*Day Progress*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfYear DATETIME;
SET @FirstDateOfYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

DECLARE @LastDateOfYear DATETIME;
SET @LastDateOfYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),12,31,0,0,0,0));

DECLARE @At INT;
SET @At = (SELECT COUNT(*) FROM [Date] WHERE [Work] = 1 AND [Date] BETWEEN @FirstDateOfYear AND @Date)

DECLARE @Total INT;
SET @Total = (SELECT COUNT(*) FROM [Date] WHERE [Work] = 1 AND [Date] BETWEEN @FirstDateOfYear AND @LastDateOfYear)

SELECT DISTINCT @At [At], @Total [Total] 
FROM [BranchTargetByYear]
WHERE [Year] = YEAR(@Date)


END
