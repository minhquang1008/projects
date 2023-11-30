/*YTD - BOM - CoSo*/

/*Trailing - New Accounts*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATETIMEFROMPARTS(YEAR(@Date)-4,1,1,0,0,0,0);

WITH 

[BranchList] AS (
	SELECT [BranchID]
	FROM [BranchTargetByYear] 
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'New Accounts'
)

, [YearlyTarget] AS (
    SELECT 
		[Year]
        , SUM(CAST([Target] AS FLOAT)) [Target]
	FROM [DWH-AppData].[dbo].[BMD.FlexTarget]
	WHERE [Year] BETWEEN YEAR(@Since) AND YEAR(@Date)
        AND [Measure] = 'New Accounts'
	GROUP BY [Year]
)

, [RRE0386.Flex] AS (
	SELECT
		[AUTOID]
		, MIN([AUTOID]) OVER (PARTITION BY [SoTaiKhoan], [NgayMoTK]) [MinID]
		, [NgayMoTK]
		, [SoTaiKhoan]
		, [IDNhanVienMoTK]
	FROM [RRE0386]
	WHERE [RRE0386].[NgayMoTK] BETWEEN @Since AND @Date
		AND [RRE0386].[IDNhanVienHienTai] IS NOT NULL
)

, [FindLastBranchID] AS (
	SELECT DISTINCT
		[relationship].[date]
		, [relationship].[account_code] [SoTaiKhoan]
		, [broker_id]
		, LAST_VALUE([branch_id]) OVER(PARTITION BY [account_code], [broker_id] ORDER BY [account_code]) [branch_id]
	FROM [relationship]
	WHERE [relationship].[date] BETWEEN @Since AND @Date
		AND [relationship].[account_code] IN (SELECT [SoTaiKhoan] FROM [RRE0386.Flex])
)

, [Rel] AS (
	SELECT
		[Date]
		, [SoTaiKhoan]
		, CASE
			WHEN [broker_id] IS NULL AND [date] <> @Date THEN LEAD([branch_id]) OVER (PARTITION BY [SoTaiKhoan] ORDER BY [date])
			ELSE [branch_id]
		END [BranchID]
	FROM [FindLastBranchID]
)

, [_RRE0386] AS (
	SELECT
		[NgayMoTK]
		, [SoTaiKhoan]
		, [IDNhanVienMoTK]
	FROM [RRE0386.Flex]
	WHERE [MinID] = [AUTOID]
)

, [ValueAllBranchesByDate] AS (
	SELECT
		DATETIMEFROMPARTS(YEAR([_RRE0386].[NgayMoTK]),12,31,0,0,0,0) [Date]
		, COUNT(*) [Actual]
	FROM [_RRE0386]
	LEFT JOIN [Rel]
		ON [Rel].[SoTaiKhoan] = [_RRE0386].[SoTaiKhoan]
		AND [Rel].[Date] = [_RRE0386].[NgayMoTK]
	WHERE [Rel].[BranchID] IN (SELECT [BranchID] FROM [BranchList])
	GROUP BY DATETIMEFROMPARTS(YEAR([_RRE0386].[NgayMoTK]),12,31,0,0,0,0)
)

SELECT
	[ValueAllBranchesByDate].[Date]
	, [ValueAllBranchesByDate].[Actual]
	, [YearlyTarget].[Target]
FROM [YearlyTarget]
LEFT JOIN [ValueAllBranchesByDate]
	ON YEAR([ValueAllBranchesByDate].[Date]) = [YearlyTarget].[Year]
ORDER BY 1


END