/*MTD - BOM - CoSo*/

/*Actual vs Target - Interest Income (Lãi vay ký quỹ - Thực tế và chỉ tiêu)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

WITH

[BadDebt] AS (
	SELECT 
		CONVERT(VARCHAR(7), [Ngay], 126) [Ngay]
		, [SoTaiKhoan]
	FROM [BadDebtAccounts]
	WHERE [Ngay] BETWEEN DATEADD(MONTH, -1, @FirstDateOfMonth) AND @Date
		AND [LoaiNo] NOT IN (N'Hết nợ', N'TK đã đóng')
)

, [TargetByBranch] AS (
    SELECT 
        [BranchID] 
        , CAST(CAST([Target] AS FLOAT) / 12 AS DECIMAL(30,8)) [InterestIncome]
    FROM [DWH-AppData].[dbo].[BMD.FlexTarget]
    WHERE [Year] = YEAR(@Date)
        AND [Measure] = 'Interest Income'
)

, [BranchActual] AS (
    SELECT 
        [relationship].[branch_id] [BranchID]
        , SUM(CASE WHEN [BadDebt].[SoTaiKhoan] IS NULL THEN [rln0019].[interest] ELSE 0 END) [InterestIncome]
    FROM [rln0019]
    LEFT JOIN [relationship]
        ON [rln0019].[date] = [relationship].[date]
        AND [rln0019].[sub_account] = [relationship].[sub_account]
	LEFT JOIN [BadDebt]
		ON [BadDebt].[SoTaiKhoan] = [relationship].[account_code]
		AND [BadDebt].[Ngay] = CONVERT(VARCHAR(7), DATEADD(MONTH, -1, [rln0019].[date]), 126)
    WHERE [rln0019].[date] BETWEEN @FirstDateOfMonth AND @Date
    GROUP BY [relationship].[branch_id]
)

SELECT
	[TargetByBranch].[BranchID]
	, ISNULL([BranchActual].[InterestIncome],0) [Actual]
    , [TargetByBranch].[InterestIncome] [Target]
FROM [TargetByBranch]
LEFT JOIN [BranchActual]
    ON [TargetByBranch].[BranchID] = [BranchActual].[BranchID]
ORDER BY 1


END
